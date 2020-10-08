import pandas as pd, numpy as np, os
import geopandas as gpd

class TaxiBlockCount:

	def __init__(self, path):
		self.path = path
		# We specify these to speed up the parsing process. Otherwise pandas would have to infer them itself
		self.column_dtypes = {'VendorID' : int, 'tpep_pickup_datetime' : None, 'tpep_dropoff_datetime' : None,
		               'passenger_count': int, 'trip_distance': float, 'pickup_longitude' : float,
		               'pickup_latitude': float, 'RateCodeID': int, 'store_and_fwd_flag': str,
		               'dropoff_longitude': float, 'dropoff_latitude': float, 'payment_type': int, 'fare_amount': float,
		               'extra': float, 'mta_tax': float, 'tip_amount': float, 'tolls_amount': float,
		               'improvement_surcharge': float, 'total_amount': float}
		self.col_names = list(self.column_dtypes.keys())
		# New York map by blocks
		self.nymap = gpd.read_file(os.path.join(path,"nyc_cbg_geoms.geojson"))
		self.nymap["geoid"] = self.nymap["geoid"].astype(np.int64)

		# New York socio-economic data
		self.acs = pd.read_csv(os.path.join(path,"nyc_acs_demographics.csv"), dtype = {"geoid" : np.int64}, index_col=0)





	def process_files(self):

		self.boundary_coordinates = self.compute_boundaries()

		file_folder = os.path.join(self.path,"data")
		print(file_folder)
		count = 0.
		files = os.listdir(file_folder)

		for file in files:
		    print("{:.2%}".format(float(count)/len(files)))
		    count +=1
		    skip_header = 1 if file.endswith("00") else None #if the file has headers then skip first row
		    df = pd.read_csv(os.path.join(file_folder,file),
		                     dtype = self.column_dtypes,
		                     names = self.col_names,
		                     skiprows = skip_header,
		                     parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime" ])
		    
		    df_clean = self.data_cleaning(df)
		    df_merged = self.spatial_merging(df_clean)
		    self.compute_pickups(df_merged, file + "_pickups.csv", "D://data_juanluis//")




	def compute_boundaries(self):
		ny_coordinates = np.array([ list(polygon.bounds) for polygon in self.nymap["geometry"].values]).T
		min_lon = ny_coordinates[0].min()
		max_lon = ny_coordinates[2].max()
		min_lat = ny_coordinates[1].min()
		max_lat = ny_coordinates[3].max()
		boundary_coordinates = (min_lat, min_lon, max_lat , max_lon)
		return boundary_coordinates


	def data_cleaning(self,df):

		# There are very few rows with null values (3 in total) We drop them.
		df.dropna(inplace = True)

		# We drop the rows which have a pickup time which comes after dropoff
		back_in_time = df[df.tpep_pickup_datetime > df.tpep_dropoff_datetime]
		df = df.drop(back_in_time.index)
		back_in_time.head(5)

		# We drop rows with negative amounts in these features
		negative_amounts = (df[["tip_amount", "tolls_amount", "total_amount", "fare_amount", "extra", "improvement_surcharge"]] < 0)
		df = df.drop(df[negative_amounts.any(axis = 1)].index)
		# We filter rows whose RateCodeId is invalid
		df = df[df["RateCodeID"].apply(lambda x : x in [1,2,3,4,5,6])]

		min_lat, min_lon, max_lat , max_lon = self.boundary_coordinates 
		# We drop rows which have coordinates outside the boundaries of the NY map
		df = df[(df[["pickup_latitude","dropoff_latitude"]] >= min_lat).any(axis = 1)]
		df = df[(df[["pickup_latitude","dropoff_latitude"]] <= max_lat).any(axis = 1)]
		df = df[(df[["pickup_longitude","dropoff_longitude"]] >= min_lon).any(axis = 1)]
		df = df[(df[["pickup_longitude","dropoff_longitude"]] <= max_lon).any(axis = 1)]

		return df

	def spatial_merging(self, df):

		# We transform df into a geodataframe creating points from the coordinates
		gdf= gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.pickup_longitude, df.pickup_latitude), crs = {'init': 'epsg:4326'})
		gdf.rename_geometry("pickup_geometry", inplace = True)

		#join gdf with nymap to get the geoid of each pickup by checking to which block belong each row's pickup coordinates
		spatial_join = gpd.sjoin(gdf,self.nymap, how = "inner", op = "within")
		spatial_join.rename(columns = {"geoid": "geoid_pickup"}, inplace = True)
		spatial_join.drop(["index_right"], axis = 1, inplace = True)

		# We merge the dataset with acs first for the pickup locations 
		df_merged = pd.merge(spatial_join, self.acs.add_suffix("_pickup"), left_on="geoid_pickup", right_on= "geoid_pickup")
		# and then for the dropoff locations 
		#df_merged = pd.merge(df_merged, acs.add_suffix("_dropoff"), left_on="geoid_dropoff", right_on= "geoid_dropoff")
		return df_merged

	def compute_pickups(self,df_merged, file_name, path):
		#"D://data_juanluis//pickup_counts.csv"
		pickups = pd.Series(data = 1, index = df_merged["geoid_pickup"].values)
		pickup_counts = pickups.groupby(level = 0).count()
		pickup_counts = pd.DataFrame(pickup_counts, columns=["count"])
		pickup_counts.to_csv(os.path.join(path,file_name))


# NY-taxi-analysis


<a  href = "https://juanluisrto.carto.com/kuviz/33e60974-6f72-49c5-89d5-e50de658eadb">
<img src="/png/map.png" width="900" height="450"/>
</a>

**[Click for live Map](https://juanluisrto.carto.com/kuviz/33e60974-6f72-49c5-89d5-e50de658eadb)** 


In this project I have explored the [TLC Trip Record Dataset](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) with data about taxi trips taken place in New York (Jan, Apr, July 2015).

It comprised 3 different steps:

### Dataset exploration and cleaning
In the first one, I check for inconsistencies in the data and perform some exploratory analysis. 
Here I also perform a spatial join between the taxi dataset and a map of the cities different blocks ([TaxiBlockCount](TaxiBlockCount.py)). I compute the average number of taxi pickups per block. 
Check out [Exploratory.ipynb](/Exploratory.ipynb) for more details.

### Modelling
I define a linear regression model in order to predict the number of taxi pickups in each specific block, taking as covariates a set of socioeconomic factors like income_per_capita, number of family_households or median_rent 
Check out [Modelling.ipynb](/Modelling.ipynb) for more details.

### Map visualization
I publish a [map](https://juanluisrto.carto.com/kuviz/33e60974-6f72-49c5-89d5-e50de658eadb) which showcases the the difference between the predictions of my model and the real valus

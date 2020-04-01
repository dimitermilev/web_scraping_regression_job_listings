# Web scraping and linear regression to predict Data Science job satisfaction

I build a web scraper to collect job and company details from Glassdoor. I then employ linear regression (simple, Ridge, Lasso) to predict satisfaction and compensation levels in Data Science jobs.

## Data

Data was scraped using Selenium and Beautiful Soup, from [Glassdoor job listings](https://www.glassdoor.com/) and [city cost of living indices](https://www.bestplaces.net). 

Approximately 2,000 job listings were scraped, and 1,000 were used in the analysis. The cost of living data was scraped for all relevant cities.

The scraped dataset included job titles and categories, salaries, benefits ratings, company reviews, company details, required skills, city information.

## Methods

**Web scraping using Beautiful Soup and Selenium**
- Browser interaction, HTML and JSON parsing to extract relevant values

**Feature engineering**
- One-hot-encoding categorical variables
- Polynomial and interaction terms

**Linear regression**
- 10-fold Cross Validation
- Use of linear regression, including Ridge and Lasso techniques to prevent overfitting

## Data manipulation and analysis

```
Selenium
Beautiful Soup
re
numpy
pandas
sklearn
```

## Front end and visualization

```
matplotlib
seaborn
Tableau
```


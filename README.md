# URL Categorizer

Contextualize URLs by grabbing site categories via the Websrhinker API and validate against a local Inclusion list. 

## Required Packages

- Pandas
- Flask
- urllib

## API Key
Note that you will need to provide your own [Webshrinker API](https://www.webshrinker.com/) key which must be imported from a config file in the same directory as main.py:

*config.py:*
```python
access_key = "your access key"
secret_key = "your secret key"
```


## Usage
After installing necessary packages and creating config.py, run main.py and point your browser to http://127.0.0.1:5000/
### Main Page
Enter your the URL you wish to look up and hit 'Submit URL'. The app will pull the IAB categorizations from from Webshrinker. Webshrinker descriptions are as follows:

| Field       | Description |
| ----------- | ----------- |
| Categories  | Human friendly label for the detected category. This doesn’t include the label of the parent category.|
| Score | A floating point number that indicates how much confidence is given to the category selection. |
|IAB Category |The IAB category identifier.|
| Confident  | If set to true, this indicates that the majority of the analyzed content relates to this category. Categories with the ‘confident’ flag can be useful to indicate primary from secondary categories. |

Upon successful submission you will also see a notification as to whether or not your provided URL is on the local inclusion list. The inclusion list is located at:
```bash
/static/sites.csv
```

If there is an API error it will be provided in this area.
### Modify Whitelist
You can view the local inclusion list in a table on the bottom of this page. If you would like to add/remove any URLs you can do so by submitting the URL to the appropriate form field. 

Upon submission you will be taken to a confirmation screen notifying you of success (successful addition/removal) or failure (attempting to add a site that is already on the inclusion list, or attempting to remove a site that is not on the inclusion list to begin with). 

After 2 seconds you will be redirected to the 'modify whitelist' page again.

## Batch Process
Batch process allows you to process your own csv files to either add the sites to the inclusion list or append columns to the raw file with inclusion list validation and Webshrinker categorization. 

When processing your csv file please ensure that the URLs are in the first column and there is 1 header row (column name does not matter) 

Simply select 'Choose File' in the appropriate section and an explorer window will open allowing you to select your file. Select upload. If you are appending to the inclusion list you will be redirected to that page. If you are adding categorization, after the file processes it will download 'file.csv' on the same page with your new columns appended to it.

## License
Artistic

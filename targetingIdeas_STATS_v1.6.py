
"""
created by Dimitrios Panourgias
June 2020

DON'T FORGET TO UPDATE THE yaml WITH A PRODUCTION AD ACCOUNT ID
OTHERWISE YOU WILL GET DUMMY STATS FROM THE TEST ACCOUNT

Months are displayed with integers
1 is the most recent month (last before current)

If you want the seed queries CSV to be user friendly
populate the locDict & langDict with as many
location and language codes as possible

"""

from googleads import adwords
import pandas as pd

# Optional AdGroup ID used to set a SearchAdGroupIdSearchParameter.
# DO NOT add ad group ID except if advised from the Performance Marketing Manager
AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
PAGE_SIZE = 10
seedCSV = pd.read_csv('targIdeasQueries.csv', header=None)
seedList = seedCSV[0].tolist()
locList = seedCSV[1].tolist()
langList =  seedCSV[2].tolist()
df = pd.DataFrame(columns=['query', 'competition', 'avg_cpc','1', '2', '3', '4', '5', '6',
                               '7', '8', '9', '10', '11', '12'])

def mainStats(client, dt, query, loc, lang, ad_group_id=None):

  locDict = {'france': 2250}
  langDict = {'french': 1002}

  # Initialize appropriate service.
  targeting_idea_service = client.GetService(
      'TargetingIdeaService', version='v201809')

  # Construct selector object and retrieve related keywords.
  selector = {
      'ideaType': 'KEYWORD',
      'requestType': 'STATS'
  }

  selector['requestedAttributeTypes'] = [
      'KEYWORD_TEXT', 'TARGETED_MONTHLY_SEARCHES', 'COMPETITION', 'AVERAGE_CPC']

  offset = 0
  selector['paging'] = {
      'startIndex': str(offset),
      'numberResults': str(PAGE_SIZE)
  }

  selector['searchParameters'] = [{
      'xsi_type': 'RelatedToQuerySearchParameter',
      'queries': query
  }]

  # Language setting (optional).
  try:
    selector['searchParameters'].append({
      # The ID can be found in the documentation:
      # https://developers.google.com/adwords/api/docs/appendix/languagecodes
      'xsi_type': 'LanguageSearchParameter',
      'languages': [{'id': langDict[lang]}]
    })
  except:
    print('Please specify language for all seed queries')

  # Location setting (optional).
  try:
    selector['searchParameters'].append({
      # The ID can be found in the documentation:
      # https://developers.google.com/adwords/api/docs/appendix/languagecodes
      'xsi_type': 'LocationSearchParameter',
      'locations': [{'id': locDict[loc]}]
    })
  except:
      print('Please specify location for all seed queries')

  # Network search parameter (optional)
  selector['searchParameters'].append({
      'xsi_type': 'NetworkSearchParameter',
      'networkSetting': {
          'targetGoogleSearch': True,
          'targetSearchNetwork': False,
          'targetContentNetwork': False,
          'targetPartnerSearchNetwork': False
      }
  })

  # Use an existing ad group to generate ideas (optional)
  if ad_group_id is not None:
    selector['searchParameters'].append({
        'xsi_type': 'SeedAdGroupIdSearchParameter',
        'adGroupId': ad_group_id
    })

  df_add = pd.DataFrame(columns=['query', 'competition', 'avg_cpc', '1', '2', '3', '4', '5', '6',
                             '7', '8', '9', '10', '11', '12'])


  more_pages = True
  while more_pages:
    page = targeting_idea_service.get(selector)

    # Display results.
    if 'entries' in page:
      for result in page['entries']:
        attributes = {}
        for attribute in result['data']:
          attributes[attribute['key']] = getattr(
              attribute['value'], 'value', '0')
        x = attributes['TARGETED_MONTHLY_SEARCHES']
        df_add = df_add.append({'query': attributes['KEYWORD_TEXT'],
                              'competition': round(attributes['COMPETITION'] * 100, 2),
                              'avg_cpc': round(attributes['AVERAGE_CPC']['microAmount'] / 1000000, 2),
                              '1': x[0]['count'],
                              '2': x[1]['count'],
                              '3': x[2]['count'],
                              '4': x[3]['count'],
                              '5': x[4]['count'],
                              '6': x[5]['count'],
                              '7': x[6]['count'],
                              '8': x[7]['count'],
                              '9': x[8]['count'],
                              '10': x[9]['count'],
                              '11': x[10]['count'],
                              '12': x[11]['count']}, ignore_index=True)
        dt = pd.concat([dt, df_add], axis=0, ignore_index=True)
      print
    else:
      print('No related keywords were found.')
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])
  return dt

if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  it = 0
  for searchTerm in seedList:
    if it == 0:
      endStats = mainStats(adwords_client, df, searchTerm, locList[it], langList[it], int(AD_GROUP_ID) if AD_GROUP_ID.isdigit() else None)
      it += 1
    else:
      endStats = mainStats(adwords_client, endStats, searchTerm, locList[it], langList[it], int(AD_GROUP_ID) if AD_GROUP_ID.isdigit() else None)
      it += 1

  print(endStats)
  endStats.to_csv('targIdeasSTATSResults.csv')

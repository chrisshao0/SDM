from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow



def get_credentials():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
    creds = flow.run_local_server(port=0)
    return creds


creds = get_credentials()

 
client = gspread.authorize(creds)


sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1BJmx9pGQnblZBfYhFVnHNprXLdYse8Li77SAn6w4Zrg/edit#gid=65656897')


sheet_instance = sheet.worksheet('Thetie')


sheet_instance.clear()

driver = webdriver.Chrome('/path/to/chromedriver') 



driver.get('https://terminal.thetie.io/users/sign_in')


username = driver.find_element(By.ID,'user_email')
password = driver.find_element(By.ID,'user_password')


username.send_keys('yacine@securedigitalmarkets.com')
password.send_keys('TheTie123!')


login_button = driver.find_element(By.ID,'user_submit')
login_button.click()

time.sleep(5) 


coin_link = driver.find_element(By.CSS_SELECTOR, "#app > div > div.bg-gray-800\/50 > div > div.tiedy-flex.tiedy-w-full.tiedy-items-center.tiedy-justify-between.tiedy-space-x-2.tiedy-text-sm.tiedy-text-slate-100.ml-6 > div > div:nth-child(7) > div > a > div.flex.items-center")
coin_link.click()

time.sleep(5)  


xpath_base = '/html/body/div[1]/div/div[2]/div[2]/div[1]/div[3]/component/div[2]/div/div/div/div/div/div[1]/div[2]/div[3]/div[1]/div/div[1]/div[{}]/div[3]/a/div/div[1]/div/div'


for i in range(1, 21):  
    
    coin_xpath = xpath_base.format(i)

    
    coin_tab = driver.find_element(By.XPATH, coin_xpath)
    coin_tab.click()

    time.sleep(5)  

    
    market_section = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[2]/div/div/div[2]/span/div[1]')
    market_section.click()

    time.sleep(5)  

    
    wait = WebDriverWait(driver, 10)

    
    title = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div/div[1]/div[1]/span[2]')))

    
    table = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div[1]/div/div[2]/div')))

    
    rows = table.find_elements(By.TAG_NAME, "div")  
    

    data=[]
    row_data=[]
    for row in rows:
        
        components = row.text.split('\n')

        
        if len(components) == 5:
            label, value1, value2, value3, value4 = components
            data.append([label, value1, value2, value3, value4])
    df = pd.DataFrame(data, columns=['Label', 'Value1', 'Value2', 'Value3', 'Value4'])
    additional_data = {}
    xpaths = {
        'coin_name': '/html/body/div[1]/div/div[2]/div[2]/div[1]/div[1]/div/div/div[1]/div[1]/span[2]',
        'all_time_high': ['/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/table/tr[1]/td[1]', '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/table/tr[1]/td[2]/span'],
        'down_from_ATH': ['/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/table/tr[2]/td[1]', '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/table/tr[2]/td[2]/span'],
        'market_cap': ['/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[1]/td[1]', '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[1]/td[2]'],
        'trading_volume': ['/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[4]/td[1]', '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[4]/td[2]/span'],
        '30d_avg_volume': ['/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[5]/td[1]', '/html/body/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div[2]/div/div[2]/table/tr[5]/td[2]/span']
    }
    for key, value in xpaths.items():
        if isinstance(value, list):
            additional_data[key] = [driver.find_element(By.XPATH, value[0]).text, driver.find_element(By.XPATH, value[1]).text]
        else:
            additional_data[key] = driver.find_element(By.XPATH, value).text
    df_additional = pd.DataFrame(additional_data).T.reset_index()
    df_additional.columns = ['Label', 'Value1', 'Value2']      
    df = pd.concat([df_additional, df], ignore_index=True)  
    print(df)
    # for i, row in df.iterrows():
    #     # gspread uses 1 based indexing (the first row and column is 1)
    #     for j, value in enumerate(row):
    #         sheet_instance.update_cell(i+2, j+1, value)
    
    values = df.astype(str).values.tolist()

    if i == 1:
        values.insert(0, df.columns.tolist())

    last_row = len(sheet_instance.get_all_values())
    start_row = last_row + 1  
    end_row = start_row + len(values) - 1  
    range_str = 'A' + str(start_row) + ':' + 'E' + str(end_row)

    
    sheet_instance.update(range_str, values)

    coin_link = driver.find_element(By.CSS_SELECTOR, "#app > div > div.bg-gray-800\/50 > div > div.tiedy-flex.tiedy-w-full.tiedy-items-center.tiedy-justify-between.tiedy-space-x-2.tiedy-text-sm.tiedy-text-slate-100.ml-6 > div > div:nth-child(7) > div > a > div.flex.items-center")
    coin_link.click()
    time.sleep(5)

print("web scripting finish")
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def chrome_nav():
    # Chrome
    service_webdriver = webdriver.ChromeService(
        ChromeDriverManager().install())
    chrome_opt = webdriver.ChromeOptions()
    chrome_opt.add_argument('--headless=new')
    chrome_opt.add_argument("--disable-gpu")
    chrome_opt.add_argument("--disable-infobars")
    chrome_opt.add_argument("--disable-notifications")
    chrome_opt.add_experimental_option("prefs", {"download.prompt_for_download": False,
                                                    "download.directory_upgrade": True,
                                                    "safebrowsing.enabled": False,
                                                    "browser.show_self_contained_ui": False,
                                                    "download.open_panel_when_showing": False})
    
    return webdriver.Chrome(service=service_webdriver, options=chrome_opt)

def edge_nav():
    # Edge
    service_webdriver = webdriver.EdgeService(
        EdgeChromiumDriverManager().install())
    edge_opt = webdriver.EdgeOptions()
    edge_opt.add_argument("--headless=new")
    edge_opt.add_experimental_option("prefs", {"download.prompt_for_download": False})
    
    return webdriver.Edge(service=service_webdriver, options=edge_opt)
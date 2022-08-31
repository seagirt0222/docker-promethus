import requests
import yaml
import os

def GetTemplateyml(Path):
    with open(Path, "r") as stream:
        yml = yaml.load(stream)
        return yml

def SetHttpyml(tmpyml):
    if tmpyml == None: 
        tmpyml= GetTemplateyml()    
    tmpyml[0]["targets"] = DomainName
    with open(savePath,"w") as f:
        yaml.dump(tmpyml,f)    

def SetRules(httpCode,f):
    rule=GetTemplateyml(rulesPath)[0]
    rule["alert"]=httpCode
    rule["expr"]='probe_http_status_code{job="'+httpCode+'"} != '+f
    rule["annotations"]["httpcode"]=int(f)
    rules.append(rule)

def SetScrapeConfigs(httpCode):
    con = GetTemplateyml(scrapeconfigsPath)[0]
    con["job_name"]=httpCode
    con["params"]["module"]=[httpCode]
    con["file_sd_configs"][0]["files"]=["/etc/prometheus/"+httpCode+".yml"]
    prome["scrape_configs"].append(con)

def SetCatblackbox():
    catblackboxs["groups"][0]["rules"] = rules
    with open("volumes/"+formal+"/catblackbox.yml","w") as c:
        yaml.dump(catblackboxs,c)    

def SetBlackbox(httpCode,code):
    modules["modules"][httpCode]= {
        "prober": "http",
        "timeout": "5s",
        "http":{
            "valid_status_codes":[int(code)],
            "valid_http_versions": ["HTTP/1.1", "HTTP/2.0"],
            "no_follow_redirects": False,
            "preferred_ip_protocol": "ip4",
            "tls_config":{
                "insecure_skip_verify": True,
            }
        }
    }
    
def SetConfig():
    with open("volumes/"+formal+"/prometheus.yml","w") as p:
        yaml.dump(prome,p) 

def SetBlackboxyml():
    with open("volumes/"+blackbox+"/blackbox.yml","w") as p:
        yaml.dump(modules,p)     

formal="prometheus"
tmp="templates"
blackbox="blackbox_exporter"
ymlPath="volumes/"+tmp+"/httpcode.yml"
scrapeconfigsPath="volumes/"+tmp+"/scrapeconfigs.yml"
catblackboxPath="volumes/"+tmp+"/catblackbox.yml"
rulesPath="volumes/"+tmp+"/rules.yml"
prometheusPath="volumes/"+tmp+"/prometheus.yml"
blackboxPath="volumes/"+tmp+"/blackbox.yml"
GetAllUrl='http://10.5.50.200:5000/api/Monitor/GetAll'

tmpyml= GetTemplateyml(ymlPath)
# config= GetTemplateyml(scrapeconfigsPath)
catblackboxs= GetTemplateyml(catblackboxPath)
# rulesTmp= GetTemplateyml(rulesPath)
blackboxTmp= GetTemplateyml(blackboxPath)
prome= GetTemplateyml(prometheusPath)
rules=[]
configs=[]
Blackboxs=[]
modules={"modules":{}}

dir = "volumes/"+formal
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

dir="volumes/"+blackbox
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

r = requests.get(GetAllUrl)
data = r.json()

HttpStatusCode = set([x["HttpStatusCode"] for x in data["ResultMessage"] if x["HttpStatusCode"] != ""])
for f in HttpStatusCode:
    #DomainName = [x["HttpType"] + "://" + x["DomainName"] for x in data["ResultMessage"] if x["HttpStatusCode"] == f]
    DomainName = [x["DomainName"] for x in data["ResultMessage"] if x["HttpStatusCode"] == f]
    savePath="volumes/"+formal+"/http_"+f+".yml"
    httpCode="http_"+f
    #依 HttpCode 建立HttpCode yml
    SetHttpyml(tmpyml)
    SetRules(httpCode,f)
    SetScrapeConfigs(httpCode)
    SetBlackbox(httpCode,f)

SetCatblackbox()
SetConfig()
SetBlackboxyml()
print("OK")
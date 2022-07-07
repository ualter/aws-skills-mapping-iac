# from dataclasses import dataclass
# import yaml, json
# import os
# from typing import Dict, Tuple
# from environment import Stages

# @dataclass
# class ConfigurationStage():
#     Name: str
#     Configuration: Dict

# class ConfigurationLoader:

#     CONFIG_PATH = "./configuration"

#     def __init__(self) -> None:
#         self.configurations = {}
#         self.configurations["default"]      = {}
#         self.configurations[Stages.DEV]     = {}
#         self.configurations[Stages.PREPROD] = {}
#         self.configurations[Stages.PROD]    = {}

#         self.load()
#         self.merge()
        
#     def load(self) -> None:
#         self.configurations["default"],      file_origin_default = self.load_config("default.yml")
#         self.configurations[Stages.DEV],     file_origin_dev     = self.load_config("dev.yml"    ,"environments")
#         self.configurations[Stages.PREPROD], file_origin_preprod = self.load_config("preprod.yml","environments")
#         self.configurations[Stages.PROD],    file_origin_prod    = self.load_config("prod.yml"   ,"environments")

#         self.configurations["default"]["origin"]      = file_origin_default
#         self.configurations[Stages.DEV]["origin"]     = file_origin_dev
#         self.configurations[Stages.PREPROD]["origin"] = file_origin_preprod
#         self.configurations[Stages.PROD]["origin"]    = file_origin_prod
    
#     def merge(self) -> None:
#         self.merge_dict(self.configurations[Stages.DEV],     self.configurations["default"])
#         self.merge_dict(self.configurations[Stages.PREPROD], self.configurations["default"])
#         self.merge_dict(self.configurations[Stages.PROD],    self.configurations["default"])
    
#     def load_config(self, file_name: str, *paths: str) -> Tuple[Dict, str]:
#         path = [self.CONFIG_PATH]
#         if (len(paths) > 0 ):
#             path.append(*paths)
#         path.append(file_name)
#         file_path = os.path.join(*path)
#         if os.path.exists(file_path):
#             with open(file_path) as f:
#                 return yaml.load(f, Loader=yaml.FullLoader), file_path
#         else:
#             return {}, file_path

#     def merge_dict(self, d1, d2):
#         if ( d1 and d2 and len(d1) > 0 and len(d2) > 0 ):
#             for k, v2 in d2.items():
#                 v1 = d1.get(k)
#                 if ((isinstance(v1, Dict)) and isinstance(v2, Dict)):
#                     self.merge_dict(v1, v2)
#                 else:
#                     if (k not in d1):
#                         d1[k] = v2

#     def get_configuration(self, stage: Stages) -> ConfigurationStage:
#         cfg = self.configurations[stage]
#         configuration_stage = ConfigurationStage(
#             stage.value, 
#             cfg
#         )
#         return configuration_stage

#     def pretty_print(self, d):
#         print(json.dumps(d,sort_keys=True, indent=4))
    
#     def print_all(self):
#         print("---------------------------------------------------")
#         print("------------------------------------------> DEFAULT")
#         self.pretty_print(self.configurations["default"])
#         print("---------------------------------------------------")
#         print("----------------------------------------------> DEV ")
#         self.pretty_print(self.configurations[Stages.DEV])
#         print("---------------------------------------------------")
#         print("------------------------------------------> PREPROD ")
#         self.pretty_print(self.configurations[Stages.PREPROD])
#         print("---------------------------------------------------")
#         print("---------------------------------------------> PROD")
#         self.pretty_print(self.configurations[Stages.PROD])
#         print("---------------------------------------------------")
#         print("")

# def main():

#     loader = ConfigurationLoader()
#     print(loader.get_configuration(Stages.DEV))
#     print(loader.get_configuration(Stages.PREPROD))

#     # print(f'DEFAULT...: {default["environment"]["account"]}')
#     # print(f'DEV.......: {dev["environment"]["account"]}')
#     # print(f'PREPROD...: {preprod["environment"]["account"]}')




# if __name__ == '__main__':
#     main()
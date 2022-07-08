from dataclasses import dataclass
import yaml, json
import os
from typing import Dict, Tuple, Any, List
from stages import Stages

@dataclass
class ConfigurationEnvironment:
    Account: str
    Region: str

@dataclass
class ConfigurationStageWebSite:
    BucketPrefix: str

@dataclass
class ConfigurationPipeline:
    Owner: str
    Name: str
    Branch: str
    SecretNameOauthToken: str
    Environment: ConfigurationEnvironment
    Origin: str

@dataclass
class ConfigurationStage:
    Name: str
    Environment: ConfigurationEnvironment
    WebSite: ConfigurationStageWebSite
    Origin: str


class ConfigurationLoader:

    CONFIG_PATH = "./configuration"
    # CONFIG_PATH = "./aws-skills-mapping-iac/configuration"

    def __init__(self) -> None:
        self.configurations = {}                  # type: Dict[Any, Any]
        self.configurations[Stages.DEV]      = {}
        self.configurations[Stages.PREPROD]  = {}
        self.configurations[Stages.PROD]     = {}
        self.configurations[Stages.DEFAULT]  = {}
        self.configurations[Stages.PIPELINE] = {}
        
        self.load()
        self.merge()
        
    def load(self) -> None:
        self.configurations[Stages.DEFAULT],  file_origin_default  = self.load_config("default.yml")
        self.configurations[Stages.PIPELINE], file_origin_pipeline = self.load_config("pipeline.yml","environments")
        self.configurations[Stages.DEV],      file_origin_dev      = self.load_config("dev.yml"     ,"environments")
        self.configurations[Stages.PREPROD],  file_origin_preprod  = self.load_config("preprod.yml" ,"environments")
        self.configurations[Stages.PROD],     file_origin_prod     = self.load_config("prod.yml"    ,"environments")

        self.configurations[Stages.DEV]["origin"]      = file_origin_dev
        self.configurations[Stages.PREPROD]["origin"]  = file_origin_preprod
        self.configurations[Stages.PROD]["origin"]     = file_origin_prod
        self.configurations[Stages.DEFAULT]["origin"]  = file_origin_default
        self.configurations[Stages.PIPELINE]["origin"] = file_origin_pipeline
    
    def merge(self) -> None:
        self.merge_dict(self.configurations[Stages.DEV],     self.configurations[Stages.DEFAULT])
        self.merge_dict(self.configurations[Stages.PREPROD], self.configurations[Stages.DEFAULT])
        self.merge_dict(self.configurations[Stages.PROD],    self.configurations[Stages.DEFAULT])
    
    def load_config(self, file_name: str, *paths: str) -> Tuple[Dict[Any, Any], str]: 
        path = [self.CONFIG_PATH]
        if (len(paths) > 0 ):
            path.append(*paths)
        path.append(file_name)
        file_path = os.path.join(*path)
        if os.path.exists(file_path):
            with open(file_path) as f:
                return yaml.load(f, Loader=yaml.FullLoader), file_path
        else:
            return {}, file_path

    def merge_dict(self, d1: Dict[Any,Any], d2: Dict[Any,Any]) -> None:
        if ( d1 and d2 and len(d1) > 0 and len(d2) > 0 ):
            for k, v2 in d2.items():
                v1 = d1.get(k)
                if ((isinstance(v1, Dict)) and isinstance(v2, Dict)):
                    self.merge_dict(v1, v2)
                else:
                    if (k not in d1):
                        d1[k] = v2

    def _get_configuration_member(self, stage: Stages, *attribute_path: str) -> Any:
        cfg = self.configurations[stage]

        if len(attribute_path) < 2:
            att = attribute_path[0]
            return cfg[att]
        else:
            def lookup_attribute(_cfg: Dict[Any, Any], _attribute_path: List[str]) -> Any:
                last = False
                for idx, attr in enumerate(_attribute_path):
                    if idx == (len(_attribute_path) - 1):
                       last = True    
                    if last:
                        if attr in _cfg:
                            return _cfg[attr]
                        return "None"
                    else:
                        return lookup_attribute(_cfg[attr], _attribute_path[1:])
                return f"Ops... path{_attribute_path} not found"
            return lookup_attribute(cfg, attribute_path) # type: ignore

    def get_configuration_pipeline(self) -> ConfigurationPipeline:
        # Pipeline Environment will be create in the Dev Environment
        dev_config = self.get_configuration_stage(Stages.DEV)
        pipe_env = ConfigurationEnvironment(
            Account=dev_config.Environment.Account,
            Region=dev_config.Environment.Region
        )
        cfg_pipe = ConfigurationPipeline(
            Owner=self._get_configuration_member(Stages.PIPELINE,"repository","owner"),
            Name=self._get_configuration_member(Stages.PIPELINE,"repository","name"),
            Branch=self._get_configuration_member(Stages.PIPELINE,"repository","branch"),
            SecretNameOauthToken=self._get_configuration_member(Stages.PIPELINE,"repository","secret-name-oauth-token"),
            Environment=pipe_env,
            Origin=self._get_configuration_member(Stages.PIPELINE,"origin"),
        )
        return cfg_pipe

    def get_configuration_stage(self, stage: Stages) -> ConfigurationStage:
        cfgEnvironment = ConfigurationEnvironment(
            Account=str(self._get_configuration_member(stage,"environment","account")),
            Region=str(self._get_configuration_member(stage,"environment","region"))
        )
        cfgStageWebSite = ConfigurationStageWebSite(
            BucketPrefix=str(self._get_configuration_member(stage,"website","bucket-prefix"))
        )
        configuration_stage = ConfigurationStage(
            Name=stage.value, 
            Environment=cfgEnvironment,
            WebSite=cfgStageWebSite,
            Origin=self._get_configuration_member(stage,"origin")
        )
        return configuration_stage

    def pretty_print(self, d: Dict[Any,Any]) -> None:
        print(json.dumps(d,sort_keys=True, indent=4))

    def pretty_print_stage(self, s: ConfigurationStage) -> None:
        print(f"""
 Name................: \033[0;32m{s.Name}\033[0m
 Environment:
   - Account.........: \033[0;32m{s.Environment.Account}\033[0m
   - Region..........: \033[0;32m{s.Environment.Region}\033[0m
 WebSite:
   - Bucket Prefix...: \033[0;32m{s.WebSite.BucketPrefix}\033[0m
 Origin..............: \033[0;32m{s.Origin}\033[0m
        """)
    
    def print_all(self) -> None:
        print("\033[1;34m----------------------------------------------------------------------------")
        print("-------------------------------------------------------------------> DEFAULT\033[0m")
        self.pretty_print_stage(self.get_configuration_stage(Stages.DEFAULT))
        print("\033[1;34m----------------------------------------------------------------------------")
        print("-----------------------------------------------------------------------> DEV\033[0m")
        self.pretty_print_stage(self.get_configuration_stage(Stages.DEV))
        print("\033[1;34m----------------------------------------------------------------------------")
        print("-------------------------------------------------------------------> PREPROD\033[0m")
        self.pretty_print_stage(self.get_configuration_stage(Stages.PREPROD))
        print("\033[1;34m----------------------------------------------------------------------------")
        print("----------------------------------------------------------------------> PROD\033[0m")
        self.pretty_print_stage(self.get_configuration_stage(Stages.PROD))
        print("\033[1;34m----------------------------------------------------------------------------")
        cfg_pipe = self.get_configuration_pipeline()
        print("\033[1;34m------------------------------------------------------------------> PIPELINE\033[0m")
        print(f"""
 Repository:
   - Owner....................: \033[0;32m{cfg_pipe.Owner}\033[0m
   - Name.....................: \033[0;32m{cfg_pipe.Name}\033[0m
   - Branch...................: \033[0;32m{cfg_pipe.Branch}\033[0m
   - Secret Name Oauth Token..: \033[0;32m{cfg_pipe.SecretNameOauthToken}\033[0m
 Environment:
   - Account..................: \033[0;32m{cfg_pipe.Environment.Account}\033[0m
   - Region...................: \033[0;32m{cfg_pipe.Environment.Region}\033[0m
 Origin.......................: \033[0;32m{cfg_pipe.Origin}\033[0m
        """)
        print("---------------------------------------------------")
        print("")

def main() -> None:
    loader = ConfigurationLoader()
    loader.print_all()

if __name__ == '__main__':
    main()
    
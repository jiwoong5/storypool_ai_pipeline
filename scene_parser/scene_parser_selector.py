from scene_parser.basic_scene_parser import BasicSceneParser
from scene_parser.llama_scene_parser import LlamaSceneParser

class SceneParserSelector:
    @staticmethod
    def get_parser(parser_type: str):
        if parser_type == "basic":
            return BasicSceneParser()
        if parser_type == "llama":
            return LlamaSceneParser()
        else:
            raise ValueError(f"지원되지 않는 parser_type: {parser_type}")

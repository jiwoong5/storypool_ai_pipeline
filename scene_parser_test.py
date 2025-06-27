from scene_parser.scene_parser_selector import SceneParserSelector
from scene_parser.scene_parser_manager import SceneParserManager

if __name__ == "__main__":
    parser = SceneParserSelector.get_parser(parser_type="basic")
    manager = SceneParserManager(parser)
    manager.process(input_file="scene_parser/input.txt", output_file="scene_parser/output.txt")

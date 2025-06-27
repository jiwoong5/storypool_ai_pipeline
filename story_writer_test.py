from story_writer.story_writer_selector import StoryWriterSelector
from story_writer.story_writer_manager import StoryWriterManager

if __name__ == "__main__":
    writer = StoryWriterSelector.get_writer('llama')
    manager = StoryWriterManager(writer)
    manager.process("story_writer/input.txt", "story_writer/output.txt")

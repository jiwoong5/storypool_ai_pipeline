from prompt_maker.prompt_maker_selector import PromptMakerSelector
from prompt_maker.prompt_maker_manager import PromptMakerManager

if __name__ == "__main__":
    prompt_maker = PromptMakerSelector.get_prompt_maker("llama")
    manager = PromptMakerManager(prompt_maker)
    manager.process("prompt_maker/input.txt","prompt_maker/output.txt")

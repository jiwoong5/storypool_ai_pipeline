from image_maker.image_maker_selector import ImageMakerSelector
from image_maker.image_maker_manager import ImageMakerManager

if __name__ == "__main__":
    image_maker = ImageMakerSelector.get_image_maker('dream_shaper')

    manager = ImageMakerManager(image_maker)

    generated_image = manager.process('[{"scene_number": 1, "generated_prompt": "Whimsical storybook illustration of a slim young adult woman with shoulder-length brown hair wearing a soft white nightgown and standing in front of an open window, morning light gently pouring through the translucent curtains, watercolor texture, pastel hues, gentle mood"}, {"scene_number": 2, "generated_prompt": "Dreamy storybook illustration of the same young woman, now dressed in a pale yellow sundress and sneakers, walking alongside her friends Jack, Lily, Tom, towards a blooming cherry tree, soft sunlight filtering through the leaves, watercolor style, enchanted atmosphere"}, {"scene_number": 3, "generated_prompt": "Fairytale-style storybook illustration of the young woman sitting on a bench with her friends, still wearing the yellow sundress and sneakers, smiling softly as they chat together beneath a blooming tree branch, watercolor texture, pastel colors"}, {"scene_number": 4, "generated_prompt": "Whimsical storybook illustration of the young woman standing alone in the meadow, dressed in the yellow sundress and sneakers, waving goodbye to her friends as they disappear into the distance, soft sunlight casting a warm glow over the scene, watercolor style"}, {"scene_number": 5, "generated_prompt": "Enchanted storybook illustration of the young woman sitting on the porch of her home, wearing the yellow sundress and sneakers, looking contented as she gazes out at the sky, now painted with hues of pink, orange, and purple, watercolor texture, gentle mood"}]')



from prompt_maker.prompt_maker_interface import PromptMakerInterface
from llama_tools.llama_helper import LlamaHelper
from api_caller.api_caller_selector import APICallerSelector
import json

class LlamaPromptMaker(PromptMakerInterface):
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = "http://localhost:11434/api/generate"):
        self.llm_helper = LlamaHelper(
            call_api_fn=APICallerSelector.select("llama", model=model_name, api_url=api_url)
        )
        self.main_instruction = self._get_main_instruction()
        self.caution = self._get_caution()

    def _get_main_instruction(self) -> str:
        """Scene Parser 데이터를 이미지 생성 프롬프트로 변환하는 메인 인스트럭션 (캐릭터 일관성 강화)"""
        return """You are an expert prompt engineer specializing in creating high-quality image generation prompts with strong emphasis on character consistency. Your role is to transform scene analysis data into detailed, visually compelling prompts that capture the essence of dramatic scenes while maintaining visual coherence across characters.

        ## Task: Scene-to-Image Prompt Generation with Character Consistency

        Given the scene analysis data, create a detailed image generation prompt that captures the visual essence of the scene with particular attention to character consistency and visual quality.

        ### Input Format:
        - Scene Number: [scene_number]
        - Scene Title: [scene_title]
        - Characters: [characters]
        - Location: [location]
        - Time: [time]
        - Mood: [mood]
        - Summary: [summary]
        - Dialogue Count: [dialogue_count]

        ### Step-by-Step Process (Character-First Approach):
        1. **Character Consistency Analysis**: Identify and maintain consistent visual characteristics for each character
        2. **Character Description**: Create detailed, consistent character appearances, expressions, and poses
        3. **Character Interaction**: Define spatial relationships and interactions between characters
        4. **Environment Integration**: Elaborate on setting, lighting, and atmosphere that complements characters
        5. **Composition Planning**: Determine optimal camera angle and framing that showcases character dynamics
        6. **Style & Quality Enhancement**: Choose artistic style and add technical quality modifiers
        7. **Prompt Assembly**: Combine all elements with character consistency as the foundation

        ### Character Consistency Guidelines:
        - Always describe characters with specific, consistent physical features
        - Include detailed clothing, accessories, and distinctive characteristics
        - Maintain consistent age, build, and facial features across scenes
        - Specify expressions and body language that match the scene's emotional tone
        - Avoid using character names - use descriptive phrases instead

        ### Example 1:
        **Input Scene Data:**
        - Scene Number: 3
        - Scene Title: "The Confrontation"
        - Characters: ["Alice", "Detective Park"]
        - Location: "abandoned warehouse"
        - Time: "night"
        - Mood: "tense"
        - Summary: "Alice faces Detective Park in a dimly lit warehouse, their conversation revealing hidden truths"
        - Dialogue Count: 8

        **Step-by-Step Generation:**
        1. **Character Consistency Analysis**: Two distinct characters with opposing roles - young civilian vs. authority figure
        2. **Character Description**: 
        - Alice: petite young woman, shoulder-length dark hair, wearing casual jeans and leather jacket, defensive posture, determined expression
        - Detective Park: middle-aged man, graying temples, wearing rumpled suit, authoritative stance, intense gaze
        3. **Character Interaction**: Positioned diagonally across the frame, maintaining distance, facing each other
        4. **Environment Integration**: Industrial warehouse with concrete floors, metal beams, single overhead light source
        5. **Composition Planning**: Medium shot capturing both characters, dramatic lighting creating strong shadows
        6. **Style & Quality Enhancement**: Cinematic realism with film noir influences, high contrast lighting
        7. **Prompt Assembly**:

        **Generated Prompt:** "Cinematic medium shot of a petite young woman with shoulder-length dark hair in leather jacket facing a middle-aged detective with graying temples in rumpled suit, tense confrontation in abandoned warehouse at night, dramatic overhead lighting casting long shadows across concrete floors and metal beams, film noir aesthetic, high contrast lighting, ultra-detailed, 8K resolution, professional cinematography"

        ### Example 2:
        **Input Scene Data:**
        - Scene Number: 7
        - Scene Title: "Morning Garden"
        - Characters: ["Emma", "her grandmother"]
        - Location: "flower garden"
        - Time: "early morning"
        - Mood: "peaceful"
        - Summary: "Emma and her grandmother share a quiet moment among blooming flowers as the sun rises"
        - Dialogue Count: 4

        **Step-by-Step Generation:**
        1. **Character Consistency Analysis**: Intergenerational bonding scene - young adult and elderly woman
        2. **Character Description**:
        - Emma: young woman in her twenties, long auburn hair, wearing flowing sundress, relaxed posture, gentle smile
        - Grandmother: elderly woman with silver hair in a neat bun, wearing cardigan and comfortable shoes, wise expression, gentle hands
        3. **Character Interaction**: Sitting close together on garden bench, grandmother's hand on Emma's shoulder
        4. **Environment Integration**: Blooming flower garden with roses and lavender, morning dew, soft golden sunlight
        5. **Composition Planning**: Wide shot showcasing garden setting, warm natural lighting from the side
        6. **Style & Quality Enhancement**: Impressionist painting style with soft, warm tones, artistic quality
        7. **Prompt Assembly**:

        **Generated Prompt:** "Impressionist painting style wide shot of a young woman with long auburn hair in flowing sundress sitting beside elderly woman with silver hair in neat bun wearing cardigan, peaceful moment in blooming flower garden during golden hour morning, soft sunlight filtering through rose petals and lavender, warm color palette, detailed botanical elements, oil painting texture, ultra-detailed, high artistic quality, serene composition"

        ### Technical Quality Enhancement Keywords:
        - Resolution: "8K resolution", "ultra-detailed", "high definition"
        - Lighting: "cinematic lighting", "dramatic shadows", "professional photography"
        - Style: "photorealistic", "oil painting texture", "concept art quality"
        - Composition: "professional cinematography", "perfect composition", "masterpiece"

        ### Your Task:
        Now generate an image prompt for the following scene data:

        {scene_data}

        Follow the character-first step-by-step process and provide:
        1. Your reasoning for each step with emphasis on character consistency
        2. The final generated prompt (150-300 characters)
        3. Comprehensive metadata including quality assessment

        ### Response Format (JSON):
        ```json
        {
            "scene_number": [scene_number],
            "success": true,
            "message": "Character-consistent image generation prompt created successfully",
            "generated_prompt": "[YOUR DETAILED PROMPT HERE]",
            "prompt_type": "[SCENE TYPE: dramatic/peaceful/action/romantic/etc.]",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
            "estimated_length": [CHARACTER COUNT],
            "prompt_quality_score": [0.0-1.0],
            "character_consistency_score": [0.0-1.0],
            "reasoning": {
                "character_consistency_analysis": "[Your analysis of character consistency requirements]",
                "character_description": "[Your detailed character visualization choices]",
                "character_interaction": "[Your character positioning and relationship decisions]",
                "environment_integration": "[Your environment elaboration that supports characters]",
                "composition_planning": "[Your composition decisions focused on character dynamics]",
                "style_selection": "[Your artistic style reasoning and quality enhancements]"
            }
        }
        ```

        ### Quality Guidelines:
        - Prompts should be 150-300 characters for optimal results
        - CHARACTER CONSISTENCY is the TOP PRIORITY
        - Include specific visual details and artistic style references
        - Balance scene elements without overcrowding the character descriptions
        - Use cinematographic and artistic terminology
        - Ensure prompts are clear and unambiguous
        - Quality score should reflect prompt completeness and visual potential
        - Character consistency score should reflect how well characters are described for visual coherence"""

    def _get_caution(self) -> str:
        """프롬프트 생성 시 주의사항 (캐릭터 일관성 강화)"""
        return """CRITICAL CAUTIONS FOR CHARACTER-CONSISTENT PROMPTS:
        1. **CHARACTER CONSISTENCY IS MANDATORY**: Always describe characters with specific, consistent physical features
        2. Always respond in valid JSON format exactly as specified
        3. Generate prompts that are 150-300 characters long for optimal image generation
        4. **Character descriptions must be detailed and specific**: Include age, build, hair, clothing, expressions
        5. **Never use character names** - use descriptive phrases instead (e.g., "young woman with auburn hair" not "Emma")
        6. **Maintain visual coherence**: Same character should have identical appearance across all scenes
        7. Include appropriate artistic style references (cinematic, painterly, photographic, etc.)
        8. **Character positioning and interaction** must be clearly specified
        9. Use technical quality keywords strategically: "ultra-detailed", "8K resolution", "professional photography"
        10. Quality score should be realistic (0.7-0.95 range typically)
        11. **Character consistency score** should reflect how well characters are described for visual coherence
        12. Keywords should include character-related terms alongside visual elements
        13. Focus on visual composition, lighting, mood, and artistic style that enhances character presence
        14. Ensure the prompt captures the essence of the scene's mood while maintaining character focus
        15. **Environmental elements should complement and frame the characters**, not overshadow them"""

    def get_error_response(self, error_message: str, scene_index: int = None) -> dict:
            """
            에러 발생 시 일관된 JSON 형식으로 응답 반환.
            """
            response = {
                "scene_number": scene_index if scene_index is not None else -1,
                "success": False,
                "message": f"Prompt generation failed: {error_message}",
                "generated_prompt": ""
            }
            return response

    def make_prompt(self, scene: str, scene_index: int) -> dict:
        """Scene Parser 데이터를 받아서 이미지 생성 프롬프트를 생성합니다."""
        try:
            # scene 데이터를 instruction에 삽입
            formatted_instruction = self.main_instruction.format(scene_data=scene.strip())
            
            # LlamaHelper를 사용하여 instruction 구성 및 실행
            instruction = self.llm_helper.build_instruction(
                formatted_instruction, 
                "",  # scene 데이터는 이미 main_instruction에 포함됨
                self.caution
            )
            
            # retry_and_extract를 사용하여 프롬프트 생성
            result = self.llm_helper.retry_and_get_json(
                instruction, 
                description=f"Scene {scene_index} 이미지 생성 프롬프트 생성"
            )
            
            return result
            
        except Exception as e:
            return self.get_error_response(str(e))

        """
        생성된 프롬프트들의 통계를 계산합니다.
        
        Args:
            responses (list): 응답 리스트
            
        Returns:
            dict: 통계 정보 딕셔너리
        """
        if not responses:
            return {}
        
        successful_responses = [r for r in responses if r.get('success', False)]
        
        if not successful_responses:
            return {'success_rate': 0.0, 'total_count': len(responses)}
        
        prompts = [r['generated_prompt'] for r in successful_responses]
        quality_scores = [r['metadata'].get('prompt_quality_score', 0.0) for r in successful_responses]
        lengths = [r['metadata'].get('estimated_length', 0) for r in successful_responses]
        
        return {
            'success_rate': len(successful_responses) / len(responses),
            'total_count': len(responses),
            'successful_count': len(successful_responses),
            'average_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            'average_length': sum(lengths) / len(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'optimal_length_compliance': sum(1 for l in lengths if self.optimal_prompt_length_range[0] <= l <= self.optimal_prompt_length_range[1]) / len(lengths) if lengths else 0.0
        }
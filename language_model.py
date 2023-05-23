import torch
from peft import PeftConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


class LanguageModel():
    MAX_CONTEXT_TOKENS = 1024
    
    GENERATION_PARAMS = {
        'max_new_tokens': 128,
        'do_sample': True,
        'temperature': .9,
        'eos_token_id': [203],
        'bad_words_ids': [[2]]
    }
    
    def __init__(self, peft_path: str, device: str='cpu'):
        peft_model_id = peft_path
        config = PeftConfig.from_pretrained(peft_model_id)
        self.model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path)
        self.model = PeftModel.from_pretrained(self.model, peft_model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path, truncation_side='left')

        self.tokenizer.add_special_tokens({'bos_token': '<s>', 'eos_token': '</s>'})
        
        self.model.to(device)
        
    def generate_answer(self, context: str) -> str:
        tokenized_context = self.tokenizer([context], max_length=self.MAX_CONTEXT_TOKENS, 
                                           truncation=True, return_tensors='pt')
        
        self.model.eval()
        with torch.inference_mode():
            outputs = self.model.generate(**tokenized_context, **self.GENERATION_PARAMS)
            outputs = outputs[0].detach().cpu()

        answer = self.tokenizer.decode(outputs, add_special_tokens=False)

        return answer[len(context):]
    
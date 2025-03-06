import openai
import os
import dotenv
import tiktoken

dotenv.load_dotenv()

def num_tokens_from_messages(messages, model="gpt-4o"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-4o":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")
  

class OpenAiYapper:
    def __init__(self, system_prompt = ""):
        self.system_prompt = {"role": "system", "content": system_prompt}
        try:
            self.client = openai.OpenAI(api_key=f'{os.getenv("OPENAI_API_KEY")}')
        except Exception as e:
            raise Exception(f'Failed to initialize OpenAI client:\n{e}')
    
    def chat(self, prompts: list[str]):
        try:
            allPrompts = []
            allPrompts.append(self.system_prompt)
            for prompt in prompts:
                allPrompts.append({"role" : "user", "content" : prompt})
            if num_tokens_from_messages(allPrompts) > 4000:
                raise Exception("Prompt too long")
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=allPrompts
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f'yapping.chat failed:\n{e}')
        
if __name__ == "__main__":
    yapper = OpenAiYapper(system_prompt="You will be plaing the role of a discord bot made by tymler called tymlerbot. Tymlerbot is an agent of choas hellbent on confusing everyone.")
    print(yapper.chat(["Hello", "respond with world"]))
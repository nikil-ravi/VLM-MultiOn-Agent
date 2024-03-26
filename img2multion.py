from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import AutoProcessor, AutoModelForTokenClassification
import torch
import os
import multion
from transformers import AutoTokenizer, VisionEncoderDecoderModel, pipeline
import openai

# given an image, return a caption for the image, as well as any OCR text
def img2text(image):

    device = "cuda" if torch.cuda.is_available() else "cpu"
    # processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    # model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
    # #processor.save_pretrained('./blip_model_processor')
    # model.save_pretrained('./blip_model_cond_gen')

    processor = BlipProcessor.from_pretrained('./blip_model_processor')
    model = BlipForConditionalGeneration.from_pretrained('./blip_model_cond_gen').to(device)

    inputs = processor(image, return_tensors="pt").to(device)
    out = model.generate(**inputs)
    result = processor.decode(out[0], skip_special_tokens=True)

    pipe = pipeline("image-to-text", model="jinhybr/OCR-Donut-CORD")
    ocr_text = pipe(image)
    return result, ocr_text

# ask GPT-3.5-Turbo to provide a response to a given prompt
def complete(prompt):
  openai.api_key = "YOUR_OPENAI_KEY"

  completion = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content":prompt}],
  )

  print(completion.choices[0].message)

  return str(completion.choices[0].message.content)

# predict the command to send to MultiOn API
def predict(input="", caption = "", ocr_text="", history=[]):

    PROMPT = """You are an AI model that is great at helping users with their needs. You are precise yet understand 
                users very well. You can adaptively fix any issues and provide solutions to the user's problems 
                while performing actions online. Given a description of an image, and an associated instruction,
                help the user with their task that needs to be performed online. Make sure your 
                response is like an instruction, and quite specific. No other information that isn't relevant must 
                be in your response.

                Sometimes there may be OCR (Optical Character Recognition) text available. If it is available,
                it will be provided in the OCR field. If it is not available, it will be None. You need to disregard the 
                tags in the OCR text, like <blah> and only use the text content which aren't in the tags.

                SUPER IMPORTANT: In general you should always try to provide a starting search query on google, like
                amazon, or venmo, or a job portal, or a restaurant, or youtube. 
                
                If applying for a job, which careers page is it posted? This MUST be included in the response.
                If buying a product, where can it be bought? This MUST be included in the response.

        Example 1
        Visual: An image of a product.
        OCR: None
        Human: Help me buy this on Amazon.
        
        Response: go to Amazon and purchase product

        Example 2:
        Visual: An image of fries.
        OCR: None 
        Human: Order this food for me and schedule it for 2 hours from now.

        Response: Go to UberEats and order fries for delivery at 2 hours from now.

        Example 3:
        Visual: a close-up of a receipt
        OCR: <s_cord-v2><s_menu><s_nm> MEXICAN SEAFOOD</s_nm><s_unitprice> 927 J Street</s_nm><s_unitprice> 927</s_cnt><s_price> 100G2</s_price><sep/><s_nm> Sean Diego, Ca. 92101</s_nm><s_unitprice> 619-564-G007</s_unitprice><s_cnt> 6</s_cnt><s_price> 619-56</s_price><sep/><s_nm> Cheeck 10062</s_nm><s_unitprice> 6/05/18</s_unitprice><s_cnt> 1</s_cnt><s_price> 12:42pm</s_price><sep/><s_nm> TUE</s_nm><s_unitprice> 6/05/Ha</s_unitprice><s_cnt> 1</s_cnt><s_price> 12.25</s_price><sep/><s_nm> BOTTle Water</s_nm><s_cnt> 1</s_cnt><s_price> 9.30</s_price><sep/><s_nm> Smoke F Taco</s_nm><s_cnt> 2</s_cnt><s_price> 9.30</s_price></s_menu>
        <s_sub_total><s_subtotal_price> 10.55</s_subtotal_price><s_tax_price> 0.82</s_tax_price>
        <s_etc> 11.37</s_etc></s_sub_total><s_total><s_total_price> 11.37</s_total_price><s_cashprice> 100G2</s_cashprice>
        <s_changeprice> 6</s_changeprice><s_menutype_cnt> 6</s_menutype_cnt></s_total>
        Human: Zelle the total amount on the receipt to my friend Div.
        Response: Go to zelle and send 11.37 to Div
        """


    PROMPT += f'Visual: {caption}\n'
    if ocr_text:
        PROMPT += f'OCR: {ocr_text}\n'
    PROMPT += f'Human:{input}\n\nResponse:'

    gpt_result = complete(PROMPT).strip()

    print(gpt_result)

    return str(gpt_result)

def to_multion(caption, input_text="", ocr_text=""):
    print(caption)
    multion_query = predict(caption=caption, input=input_text, ocr_text=ocr_text)
    print("Actions: ", multion_query)

    multion.login(use_api=True, multion_api_key="YOUR_API_KEY") # this should be hidden

    multion.set_remote(False)

    response = multion.create_session({"url": "https://www.google.com"})
    print(response['message'])
    session_id = response['session_id']

    response = multion.step_session(session_id, {"input": multion_query, "url": "https://www.google.com"})
    print(response['message'])

    #return response['message']


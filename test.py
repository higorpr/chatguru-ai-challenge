# Use this code block if you ONLY want to know the sentiment for each review. This code will NOT try to summarize each review.

# Create a custom function that will call the openAI API and send your reviews data to it one review at a time
# We will use the tqdm library to create a progress tracker so we can see if there are any problems with the openAI API processing our requests
def analyze_my_review(review):
    retries = 3
    sentiment = None

    while retries > 0:
        messages = [
            {"role": "system", "content": "You are an AI language model trained to analyze and detect the sentiment of product reviews."},
            {"role": "user", "content": f"Analyze the following product review and determine if the sentiment is: positive, negative or neutral. Return only a single word, either POSITIVE, NEGATIVE or NEUTRAL: {review}"}
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            # We only want a single word sentiment determination so we limit the results to 3 openAI tokens, which is about 1 word. 
            # If you set a higher max_tokens amount, openAI will generate a bunch of additional text for each response, which is not what we want it to do
            max_tokens=3,
            n=1,
            stop=None,
            temperature=0
        )

        response_text = completion.choices[0].message.content
        # print the sentiment for each customer review, not necessary but it's nice to see the API doing something :)
        print(response_text)

        # Sometimes, the API will be overwhelmed or just buggy so we need to check if the response from the API was an error message or one of our allowed sentiment classifications.
        # If the API returns something other than POSITIVE, NEGATIVE or NEUTRAL, we will retry that particular review that had a problem up to 3 times. This is usually enough.
        if response_text in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            sentiment = response_text
            break
        else:
            retries -= 1
            time.sleep(0.5)
    else:
        sentiment = "neutral"

    retries = 3
   
    # OpenAI will limit the number of times you can access their API if you have a free account. 
    # If you are using the openAI free tier, you need to add a delay of a few seconds (i.e. 4 seconds) between API requests to avoid hitting the openai free tier API call rate limit.
    # This code will still work with an openAI free tier account but you should limit the number of reviews you want to analyze (<100 at a time) to avoid running into random API problems.

    time.sleep(0.5)

    return sentiment

# Define the input file that contains the reviews you want to analyze
input_file = "reviews.csv"
# Read the input file into a dataframe
df = pd.read_csv(input_file)

# Analyze each review using ChatGPT and save the results in a list called sentiments so we can access the results later
sentiments = []

# Here we loop through all of the reviews in our dataset and send them to the openAI API using our custom function from above
for review in tqdm(df["Product_Review"], desc="Processing reviews"):
    sentiment = analyze_my_review(review)
    sentiments.append(sentiment)

# Now let's save the openAI API results as an additional column in our original dataset
df["sentiment"] = sentiments

# Save the results to a new Excel file (not a CSV file this time so it's easier for non-python users to work with)
output_file = "reviews_analyzed_full_sentiment.xlsx"
df.to_excel(output_file, index=False)


# Let's also save the results to a new Word file just in case people prefer to use that instead of Excel
output_file = "reviews_analyzed_full_sentiment.docx"
doc = docx.Document()

# Now that the Word doc has been created, we can add a table with headers
table = doc.add_table(rows=1, cols=2)
header_cells = table.rows[0].cells
header_cells[0].text = 'Product_Review'
header_cells[1].text = 'Sentiment'

# Now we add the table content to show each review and the associated sentiment that chatGPT determined
for index, row in df.iterrows():
    row_cells = table.add_row().cells
    row_cells[0].text = str(row['Product_Review'])
    row_cells[1].text = row['sentiment']

doc.save(output_file)
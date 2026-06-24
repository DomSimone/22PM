# Define the content of the .env file based on the user's provided env.txt file
env_content = """# Google Gemini API Key (Recommended — higher free tier limits)
GEMINI_API_KEY=AIzaSyBRvYT6PUq0MoLJuucJ6fTOVfKvYhzkNTc

# Groq API Key (Faster inference, lower limits)
GROQ_API_KEY=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

# LLM Models (free tier defaults — change if needed)
GEMINI_MODEL=gemini-1.5-flash
GROQ_MODEL=llama3-70b-8192

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
"""

# Write the content to a file named .env
file_path = ".env"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(env_content)

print(f"File successfully created: {file_path}")
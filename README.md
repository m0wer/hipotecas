# Spanish Mortgage Contract Analyzer

This Streamlit web application analyzes Spanish mortgage contracts for potentially abusive practices using OCR and the Anthropic AI API.

## Features

- Upload PDF files containing Spanish mortgage contracts
- Perform OCR to extract text from the PDF
- Analyze the extracted text for potentially abusive practices using Anthropic AI
- Display the analysis results, highlighting any identified issues

## Prerequisites

- Docker and Docker Compose
- Anthropic API key

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/spanish-mortgage-analyzer.git
   cd spanish-mortgage-analyzer
   ```

2. Create a `.env` file in the project root and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Build and run the Docker container:
   ```
   docker-compose up --build
   ```

4. Open your web browser and navigate to `http://localhost:8501` to access the Streamlit app.

## Usage

1. Upload a PDF file containing a Spanish mortgage contract.
2. Wait for the OCR process to complete and the AI analysis to finish.
3. Review the analysis results, which will highlight any potentially abusive practices found in the contract.

## Note

This tool is for informational purposes only and should not be considered legal advice. Always consult with a qualified legal professional for advice on your specific situation.

## License

This project is licensed under the MIT License.

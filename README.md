# **Automated Product Text Matching System**

## **Overview**

This project automates the process of matching external product names with internal product names using a combination of **vector-based similarity search** and **LLM-based validation**. It ensures that the **Manufacturer, Name, and Size** of products are identical.

## **Features**

- **User-Friendly UI**: Built with **Streamlit** for uploading files and displaying results.
- **Efficient Vector Matching**: Uses **Pinecone** to store and retrieve similar internal product embeddings.
- **LLM-Powered Validation**: Utilizes **GPT-4** for final match confirmation.
- **Batch Processing**: Supports large datasets with optimized embedding storage.
- **Downloadable Results**: Provides CSV export of matched product pairs.

## **Technology Stack**

- **Frontend**: Streamlit (User Interface)
- **Backend**: Python, Pandas
- **Vector Database**: Pinecone
- **LLM Model**: OpenAI GPT-4
- **Embedding Generation**: OpenAIEmbeddings via LangChain

## **How It Works**

1. **Upload Data**: Users upload two CSV files (internal & external product lists).
2. **Data Preprocessing**: Cleans data, removing empty rows andduplications.
3. **Vector Storage**: Internal products are embedded and stored in **Pinecone**.
4. **Matching Process**:
   - Retrieves the top **similar** internal product for each external product.
   - Passes both products to GPT-4 for validation based on attribute matching (**Manufacturer, Name, and Size**).
5. **Results Display & Export**:
   - The system shows matched results in a table.
   - Users can download the results as a CSV file.

## **Installation & Setup**

### **Prerequisites**

- Python 3.10
- OpenAI API Key
- Pinecone API Key

### **Installation Steps**

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/text-matching.git
   cd text-matching
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   export OPENAI_API_KEY='your-api-key'
   export PINECONE_API_KEY='your-api-key'
   ```
5. Run the Streamlit app:
   ```sh
   streamlit run app.py
   ```

## **Usage**

1. Open the **Streamlit UI** in the browser.
2. Upload **Internal Product List** and **External Product List** CSV files.
3. Click on **Process Matches**.
4. View results in a tabular format.
5. Download the CSV of matched products.

## **Future Enhancements**

- Improve LLM prompt engineering for better accuracy.
- Implement multi-stage filtering for more robust matching.
- Add human-in-the-loop validation for edge cases.
- Enhance Pinecone indexing for better retrieval performance.

## **Contributors**

- [Shima Aghtar]

## **License**

This project is licensed under the MIT License.

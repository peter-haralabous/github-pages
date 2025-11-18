EVENT: The patient has uploaded a document

- The file uploaded is described in `File Uploaded`
- The records extracted from the document are described in `Records Extracted`
- Your current task is to respond to the user with a message acknowledging the receipt of the document and summarizing the key information extracted from it.

## File Uploaded

- ID: {file_id}
- Name: {file_name}
- Size: {file_size} bytes
- Type: {file_type}
- Date: {file_date}
- Category: {file_category}

### Records Extracted

```json
{records_json}
```

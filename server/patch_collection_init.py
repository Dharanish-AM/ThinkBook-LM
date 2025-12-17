import os

target_file = '/Users/dharanisham/Developer/Github-Repositories/ThinkBook-LM/server/.venv/lib/python3.14/site-packages/chromadb/api/models/Collection.py'

with open(target_file, 'r') as f:
    lines = f.readlines()

new_lines = []
patched = False

for i, line in enumerate(lines):
    new_lines.append(line)
    # Look for the end of the __init__ signature to inject the super call
    # The signature ends with ): and the nex line is indented.
    # In the original file, it looks like:
    #     def __init__(
    #         self,
    #         client: "API",
    #         name: str,
    #         id: UUID,
    #         embedding_function: Optional[EmbeddingFunction] = None,
    #         metadata: Optional[Metadata] = None,
    #     ):
    #         self._client = client
    
    if line.strip() == '):' and 'def __init__' in "".join(lines[i-7:i+1]) and not patched:
        # We are at the end of __init__ definition.
        # Check if the next line is "self._client = client" (with indentation)
        if i + 1 < len(lines) and 'self._client = client' in lines[i+1]:
             # Inject super().__init__ call with correct indentation (8 spaces)
             new_lines.append('        super().__init__(name=name, id=id, metadata=metadata)\n')
             patched = True

with open(target_file, 'w') as f:
    f.writelines(new_lines)

if patched:
    print("Successfully patched Collection.py")
else:
    print("Could not find insertion point or already patched.")

#!/bin/bash
input=$(cat)

project_dir=$(python3 -c "
import json, sys
data = json.loads(sys.argv[1])
print(data.get('cwd', '.'))
" "$input")

if [ -f "$project_dir/README.md" ]; then
  exit 0
fi

echo "README.md not found in $project_dir. Create a README.md before finishing." >&2
exit 2

import re

with open('/Users/ben/Desktop/InEarSnitch/V27_MASTER_COLLECTION.scad', 'r') as f:
    v27_content = f.read()

# Extract sleeve
sleeve_match = re.search(r'module sleeve\(\) \{.*?\n\}', v27_content, re.DOTALL)
sleeve_str = sleeve_match.group(0) if sleeve_match else ""

# Extract TEIL 3 and TEIL 4
teil34_match = re.search(r'(// ==========================================\n// TEIL 3.*?)\n// ==========================================\n// TEIL 5', v27_content, re.DOTALL)
teil34_str = teil34_match.group(1) if teil34_match else ""

with open('/Users/ben/Desktop/InEarSnitch/MASTER_Silikon_Formen.scad', 'r') as f:
    master_content = f.read()

# Find insertion point: right before `// ==========================================\n// DRUCK-LAYOUT` or `if (drucke_v27_classic)`
insert_idx = master_content.find('// ==========================================\n// DRUCK-LAYOUT')
if insert_idx == -1:
    insert_idx = master_content.find('if (drucke_v27_classic)')

if insert_idx != -1:
    new_master = master_content[:insert_idx] + "\n" + sleeve_str + "\n\n" + teil34_str + "\n" + master_content[insert_idx:]
    with open('/Users/ben/Desktop/InEarSnitch/MASTER_Silikon_Formen.scad', 'w') as f:
        f.write(new_master)
    print("Successfully merged into MASTER_Silikon_Formen.scad")
else:
    print("Could not find insertion point!")

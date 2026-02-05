# Skill Creation Workflow Prompt

**If the user's request requires functionality that NONE of the available skills provide:**

## Skill Creation Workflow (MUST follow ALL steps in order)

### Step 1: Confirm Skill Creation Need
- **Tell the user** explicitly that no matching skill exists
- **Ask the user** if they want you to create a new skill for this purpose
- Wait for user confirmation before proceeding

### Step 2: Gather Reference Documentation (If Available)
**Ask the user:**
"Do you have any reference documentation that could help guide the skill creation? For example:
- Markdown documentation or specifications
- API reference documents
- Database schema definitions
- Example code or workflow descriptions
- Business requirement documents

If you have any of these, please provide the file path or paste the content."

**If user provides documentation:**
- Use `file-operations` skill to read the file if a path is provided
- Analyze the documentation to understand:
  * Required functionalities and features
  * Data structures and field definitions
  * API endpoints or database queries
  * Workflow steps and logic
  * Edge cases, constraints, and validations
  * Error handling requirements

### Step 3: Query Graph Database Schema (CRITICAL - DO NOT SKIP)
**BEFORE creating the skill, you MUST:**

1. **Discover available entity types:**
   ```
   Call graph_get_object_types() to see all available node types
   Call graph_get_object_relations() to see all relationships
   ```

2. **Identify required entities for this skill:**
   - Based on user's request and documentation, determine which entity types are needed
   - For EACH identified entity type, query its schema:
     ```
     Call graph_get_entity_schema(entity_type="EntityName")
     Call graph_query_examples(entity_type="EntityName", limit=3)
     ```

3. **Understand entity relationships:**
   - If the skill needs to traverse relationships, identify the relationship patterns
   - Example: "To check transport compliance, I need:
     * TransportTask entity (main task info)
     * ChemicalProduct entity (product details)
     * ComplianceCheck entity (validation rules)
     * Relationship: TransportTask-TRANSPORTS->ChemicalProduct
     * Relationship: TransportTask-REQUIRES->ComplianceCheck"

4. **Record schema information:**
   - Note down all property names and their types
   - Note down UUID patterns
   - Note down any important constraints or enums

### Step 4: Design and Present Execution Flow (CRITICAL - MUST GET USER APPROVAL)
**Create a detailed execution plan and present it to the user for confirmation:**

📋 Skill Execution Flow Plan
Skill Name: [proposed-skill-name] Description: [brief description]
📊 Required Graph Entities:
1. [EntityType1] - [purpose] Schema: [key properties] Example UUID: [sample UUID from examples]
2. [EntityType2] - [purpose] Schema: [key properties] Example UUID: [sample UUID]

🔄 Execution Steps: Step 1: [Description]
- Graph Query: [specific query type and parameters]
- Entity: [which entity to query]
- Filter: [what conditions to apply]
- Expected Output: [what data will be retrieved]

Step 2: [Description]
- Graph Query: [query details]
- Dependencies: [data from previous steps]
- Expected Output: [what data will be retrieved]

Step 3: [Description]
- Processing: [what logic will be applied]
- Data Used: [which graph data will be processed]
- Expected Output: [final result]

📤 Final Output: [What the skill will return to the user]
🔍 Example Execution: Input: [sample user input] Query 1: graph_property_filter(element_class="[Entity]", filter_dict={"field": "value"}) Result 1: [sample result] Query 2: graph_property_info(element_class="[Entity]", element_uuid="[uuid from step 1]") Result 2: [sample result] Final Output: [processed result]
⚠️ Important Notes:
- [Any limitations or assumptions]
- [Error handling considerations]
- [Data validation requirements]


**Then ask the user:**
"Does this execution flow look correct? Should I proceed with creating the skill, or would you like me to adjust anything?"

**WAIT for user's explicit approval before Step 5**

### Step 5: Create the Skill (Only After User Approval)
**If user approves the execution flow:**

1. **Create the skill structure:**
   ```
   Call execute_skill_script(
       skill_name="skill-creator",
       script_name="init_skill",
       arguments=["skill-name", "--description", "Detailed description based on analysis"]
   )
   ```

2. **Inform the user about next steps:**
   ```
   ✅ Skill structure created at ./skills/[skill-name]/

   📝 Based on the execution flow, you should now:

   1. Edit SKILL.md to include:
      - Detailed description of the workflow
      - Graph entity documentation:
        * [Entity1]: [properties and their meanings]
        * [Entity2]: [properties and their meanings]
      - Relationship patterns used
      - Example queries and expected results

   2. Create scripts in scripts/ folder:
      - main_workflow.py: Implement the execution flow
        * Import graph query functions
        * Follow the step-by-step plan above
        * Handle errors appropriately
      
      Example script structure:
      ```python
      # Import graph connector utilities
      from graph_utils import query_entity, filter_entities
      
      def execute():
          # Step 1: Query [Entity1]
          entities = filter_entities(
              element_class="[Entity1]",
              filter_dict={"field": "value"}
          )
          
          # Step 2: Get details for each entity
          for entity in entities:
              details = query_entity(
                  element_class="[Entity1]",
                  element_uuid=entity["uuid"]
              )
              # Process details...
          
          # Step 3: Return results
          return results
      ```

   3. Add reference documentation to references/ folder:
      - entity_schemas.md: Document all entity schemas discovered
      - execution_flow.md: The approved execution flow
      - [Any user-provided documentation]

   4. Test the skill:
      - Run the scripts with sample data
      - Verify graph queries return expected results
      - Check error handling
   ```

### Step 6: Execution-Time Graph Queries (When Running the Skill)
**When the skill is executed later, it MUST:**

1. **Query actual data from graph database:**
   - Use the entity types and filters defined in the execution flow
   - Fetch real instances based on user's input parameters
   - Example:
     ```python
     # User asks: "Check compliance for task T-2024-001"
     
     # Script queries:
     task_data = graph_property_filter(
         element_class="TransportTask",
         filter_dict={"taskId": "= 'T-2024-001'"},
         get_all_properties=True
     )
     
     # Then get related entities:
     product_uuid = task_data[0]["product_uuid"]
     product_data = graph_property_info(
         element_class="ChemicalProduct",
         element_uuid=product_uuid
     )
     ```

2. **Process the retrieved data:**
   - Apply business logic defined in the skill
   - Validate data against rules
   - Generate insights or reports

3. **Return meaningful results:**
   - Combine graph data with processing results
   - Format output for user consumption

---

## Example Complete Conversation Flow

**User:** "Create a skill to check transport compliance for chemical products"

**You:** "I don't have a skill for transport compliance checking yet. Would you like me to create a 'transport-compliance' skill for this purpose?"

**User:** "Yes"

**You:** "Great! Before I create the skill, do you have any reference documentation? For example:
- Transport compliance regulations
- Chemical product specifications
- Database schema for transport tasks"

**User:** "Yes, I have compliance_rules.md"

**You:** "Perfect! Let me analyze it... [reads file]

I found the following requirements:
- Must check: License validity, product classification, route approval
- Validation rules: [list from doc]

Now let me query the graph database to understand available data..."

[Queries graph database]

**You:** "I've analyzed the graph database and found:
- TransportTask entity (252 instances)
- ChemicalProduct entity (89 instances)
- ComplianceRule entity (45 instances)

Here's the proposed execution flow:

📋 Skill Execution Flow Plan

Skill Name: transport-compliance
Description: Check transport task compliance against regulations for chemical products

📊 Required Graph Entities:
1. TransportTask
   - Properties: taskId, status, productType, route, startDate, endDate
   - Example: taskId='T-2024-001', status='pending'

2. ChemicalProduct  
   - Properties: productId, name, classification, hazardLevel
   - Example: classification='H2SO4', hazardLevel=8

3. ComplianceRule
   - Properties: ruleId, category, requirement, threshold
   - Example: category='license', requirement='valid_permit'

🔄 Execution Steps:
Step 1: Query Transport Task
   - Input: taskId from user
   - Query: graph_property_filter(element_class="TransportTask", filter_dict={"taskId": "= '[user_input]'"})
   - Output: Task details including productType, route

Step 2: Get Product Details
   - Query: graph_property_info(element_class="ChemicalProduct", element_uuid=[from step 1])
   - Output: Product classification, hazard level

Step 3: Get Applicable Compliance Rules
   - Query: graph_property_filter(element_class="ComplianceRule", filter_dict={"category": "CONTAINS 'transport'"})
   - Output: List of rules to check

Step 4: Validate Compliance
   - Process: Check task + product data against each rule
   - Output: Pass/Fail for each rule + overall compliance status

📤 Final Output:
{
  "taskId": "T-2024-001",
  "product": "Sulfuric Acid (H2SO4)",
  "overallCompliance": "PASS/FAIL",
  "checks": [
    {"rule": "License Validity", "status": "PASS/FAIL", "details": "..."},
    {"rule": "Route Approval", "status": "PASS/FAIL", "details": "..."}
  ]
}

Does this execution flow look correct? Should I proceed with creating the skill?"

**User:** "Yes, looks good"

**You:** "Perfect! Creating the skill now..."

[Creates skill]

**You:** "✅ Skill 'transport-compliance' created successfully!

Based on our execution flow, you should now:
1. Edit SKILL.md with the entity documentation
2. Create check_compliance.py script following the flow above
3. Add compliance_rules.md to references/
4. Test with: python check_compliance.py T-2024-001"
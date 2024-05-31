#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install spacy py2neo')


# In[2]:


# Read the text file
with open('data.txt', 'r') as file:
    text = file.read()
    
print(text)    


# In[4]:


import re
from collections import defaultdict

# Split the text into lines
lines = text.split('\n')

# Initialize dictionaries for nodes and relationships
nodes = {}
relationships = []

# Process each line to extract information
for line in lines:
    # Extract name and type (girl/boy)
    if 'is a girl' in line or 'is a boy' in line:
        name = line.split(' is ')[0].strip()
        gender = 'girl' if 'girl' in line else 'boy'
        if name not in nodes:
            nodes[name] = {'label': 'Person', 'properties': {'gender': gender}}
        else:
            nodes[name]['properties']['gender'] = gender
    
    # Extract knows relationships
    elif 'knows' in line:
        parts = line.split(' knows ')
        person1 = parts[0].strip()
        person2 = parts[1].strip()
        relationships.append((person1, 'KNOWS', person2))
    
    # Extract ages
    elif 'years old' in line:
        parts = line.split(' is ')
        name = parts[0].strip()
        age = int(re.search(r'\d+', parts[1]).group())
        if name not in nodes:
            nodes[name] = {'label': 'Person', 'properties': {'age': age}}
        else:
            nodes[name]['properties']['age'] = age

# Display nodes and relationships
print("Nodes:", nodes)
print("Relationships:", relationships)


# In[5]:


from py2neo import Graph, Node, Relationship

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Clear the graph (optional)
graph.delete_all()

# Create or update nodes
for name, data in nodes.items():
    label = data['label']
    properties = data['properties']
    node = Node(label, name=name, **properties)
    graph.merge(node, label, "name")

# Create relationships
for person1, rel_type, person2 in relationships:
    node1 = graph.nodes.match("Person", name=person1).first()
    node2 = graph.nodes.match("Person", name=person2).first()
    if node1 and node2:
        rel = Relationship(node1, rel_type, node2)
        graph.merge(rel)

print("Nodes and relationships have been created in Neo4j.")


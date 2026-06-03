# This script needs to be executed twice for all parts to work.

# Create a map canvas object
mc = iface.mapCanvas()

# Get swimming pools and districts layers
pools = QgsProject.instance().mapLayersByName("public_swimming_pools")[0]
districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]

# Get all fields of the pools layer
fields = pools.fields()

# Getting access to the layers data provider
provider = pools.dataProvider()

# Getting access to the layers capabilities
capabilities = provider.capabilitiesString()
# print(capabilities)


# Add a new column called district (type string, 50 characters):

# Check if adding attributes is part of the capabilties of the layer
if "Attribute hinzufügen" in capabilities:
    print("Fields can be added to the layer.")
    
    # check if the field "district" already exists
    if "district" in fields.names():
       print("Field district already exists.") 
       
    else:
        # Create new fields
        district_field = QgsField("district", QVariant.String, len = 50)
        
        # Use the data provider to add the fields to the layer
        provider.addAttributes([district_field])
        
        # Show the new field in the layer using updateFields()
        pools.updateFields()
        
        print("Field district has been added to the layer.")
    
else:
    print("Field cannot be added to the layer.")


# Change the pools Type values based on the previous values
#(H -> Hallenbad, F -> Freibad) and fill the district column:

# Check if modifying attribute values is part of the capabilties of the layer
if "Attributwerte ändern" in capabilities:
    print("Attribute values can be modified.")
    
    for pool in pools.getFeatures():
        
        # Get the id of the current feature
        pool_id = pool.id()
        pool_geom = pool.geometry()
        
        # Translate the Type value
        if pool["Type"] == "H":
            new_type = "Hallenbad"
        elif pool["Type"] == "F":
            new_type = "Freibad"
        else: new_type = pool["Type"]
        
        # Build the change dictionary
        attributes = {fields.indexOf("Type"): new_type}
        
        # Find out which city district the pool is located in
        for district in districts.getFeatures():
            if pool_geom.within(district.geometry()):
                attributes[fields.indexOf("district")] = district["Name"]
                break
                
        # Execute both attribute value changes
        provider.changeAttributeValues({pool_id: attributes})
    
    print("All relevant features are modified.")
    
else:
    print("Features of this layer cannot be modified.")

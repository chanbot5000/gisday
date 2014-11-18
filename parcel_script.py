import arcpy, sys, os, subprocess, shutil, Tkinter
from Tkinter import *

def quit_program():
    sys.exit()

def parcelFunc():
    #remove old data
    try:
        shutil.rmtree('C:\Scratch\gis_day\data')
    except:
        pass
    
    #convert KML to layer
    print 'converting KML to layer..'
    arcpy.KMLToLayer_conversion(r'C:\Scratch\gis_day\src\poly.kml',r'C:\Scratch\gis_day\data')

    #convert layer to shapefile
    print 'converting layer to shapefile...'
    arcpy.FeatureClassToFeatureClass_conversion(r"C:\Scratch\gis_day\data\poly.gdb\Placemarks\Polygons",r"C:\Scratch\gis_day\data","poly")

    #open MXD containing template
    print 'opening MXD template...'
    template_mxd = arcpy.mapping.MapDocument(r"C:\Scratch\gis_day\parcel_template.mxd")
    template_df = arcpy.mapping.ListDataFrames(template_mxd)[0]
    parcelLayer = arcpy.mapping.ListLayers(template_mxd, "", template_df)[0]

    #perform selection by location
    print 'selecting parcels...'
    arcpy.SelectLayerByLocation_management(parcelLayer, "INTERSECT", r"C:\Scratch\gis_day\data\poly.shp")

    #extract overlapping parcels
    print 'extracting parcels...'
    arcpy.FeatureClassToFeatureClass_conversion(parcelLayer, r"C:\Scratch\gis_day\data", "selected_parcels.shp")

    #clear selection
    print 'clearing selection...'
    arcpy.SelectLayerByAttribute_management(parcelLayer, "CLEAR_SELECTION")

    #add selected parcels to MXD
    print 'adding extracted parcels...'
    addLayer = arcpy.mapping.Layer(r"C:\Scratch\gis_day\data\selected_parcels.shp")
    arcpy.mapping.AddLayer(template_df, addLayer, "TOP")

    #remove parcel layer
    arcpy.mapping.RemoveLayer(template_df, parcelLayer)
   
    #style parcel layer to match yellow line
    print 'applying style to new dataset...'
    selected_parcels = arcpy.mapping.ListLayers(template_mxd, "", template_df)[0]
    arcpy.ApplySymbologyFromLayer_management(selected_parcels, r"C:\Scratch\gis_day\src\style_template.lyr")

    #set mxd scale
    print 'setting scale...'
    layer_extent = selected_parcels.getExtent()
    template_df.extent = layer_extent
    template_df.scale = template_df.scale + 500

    #save mxd
    print 'saving mxd...'
    savePath = E2.get() + '\\' + E1.get() + '.mxd'
    template_mxd.saveACopy(savePath)

    #export as PDF
    print 'save as pdf...'
    new_mxd = arcpy.mapping.MapDocument(savePath)
    pdfName = E1.get() + '.pdf'
    underscorePDF = pdfName.replace(" ", "_")
    pdfPath = E2.get() + '\\' + underscorePDF        
    arcpy.mapping.ExportToPDF(new_mxd, pdfPath)    

    #open PDF
    print 'opening pdf...'
    os.chdir(E2.get())
    os.system("start "+underscorePDF)    

    #quit
    print 'quitting...'
    sys.exit()

#############################

#tkinter GUI design
root = Tkinter.Tk()
root.title("Parcel Map Maker")

#map title
L1 = Label(root, text="Map Title", borderwidth=5)
L1.grid(row=0,column=0)
E1 = Entry(root, bd=5)
E1.grid(row=0, column=1)

#output location
L2 = Label(root, text="Map Output Location", borderwidth=5)
L2.grid(row=1, column=0)
E2 = Entry(root, bd=5)
E2.grid(row=1, column=1)

#submit button
B2 = Button(root, text="Submit", command=parcelFunc)
B2.grid(row=2, column=0)

B3 = Button(root, text="Quit", command=quit_program)
B3.grid(row=2, column=1)

root.mainloop()

try:
    from osgeo import gdal
except:
    import gdal
try:
    from osgeo import ogr
except:
    import ogr
try:
    from osgeo import osr
except:
    import osr

from gdalconst import *
#import shlex
#import subprocess
import os
from . watershedFunctions import create_OutletShape
from usu_data_service.utils import *
from .utils import *

def get_raster_subset(input_raster=None, output_raster=None, xmin=None, ymax=None, xmax=None, ymin=None):
    #parameters are ulx uly lrx lry
    """ To Do: Boundary check-> check if the bounding box of subset raster is
               within the input_raster's boundary

    Note: upper left (ul) considered origin, i.e. xmin, ymax
    parameters passed as ulx uly lrx lry
    """
    cmdString = "gdal_translate"+" "+"-projwin"+" "+str(xmin)+" "+str(ymax)+" "\
               +str(xmax)+" "+str(ymin)+" "+input_raster+" "+output_raster

    return call_subprocess(cmdString,'get raster subset')


def rasterToNetCDF(input_raster=None, output_netcdf=None):
    cmdString = "gdal_translate -of netCDF "+input_raster+" "+output_netcdf
    return call_subprocess(cmdString, 'raster to netcdf')


def delineate_Watershed_TauDEM(input_DEM_raster=None, outletPointX=None, outletPointY=None, output_WS_raster=None,
                                       output_Outlet_shpFile=None, utmZone=None, streamThreshold=None):
    """TauDEM doesn't take compressed file; uncompress file
        ToDO:  Check compression first"""

    input_Outlet_shpFile = generate_uuid_file_path()
    print('shape_file_uuid_path:' + input_Outlet_shpFile)

    response_dict = create_OutletShape(shapefilePath=input_Outlet_shpFile, outletPointX=outletPointX, outletPointY=outletPointY)
    # print(response_dict)
    # return response_dict
    if response_dict['success'] == 'False':
        return response_dict

    input_Outlet_shpFile = os.path.join(input_Outlet_shpFile, 'outlet', 'outlet.shp')

    temp_raster = 'temp.tif'
    retDictionary = uncompressRaster(input_DEM_raster, temp_raster)
    if retDictionary['success'] == "False":
        return retDictionary

    input_raster = os.path.splitext(input_DEM_raster)[0]      #remove the .tif

    # pit remove
    cmdString = "pitremove -z "+temp_raster+" -fel "+input_raster+"fel.tif"
    retDictionary = call_subprocess(cmdString,'pit remove')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 flow dir
    cmdString = "d8flowdir -fel "+input_raster+"fel.tif -sd8 "+input_raster+"sd8.tif -p "\
                +input_raster+"p.tif"
    retDictionary = call_subprocess(cmdString, 'd8 flow direction')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 contributing area without outlet shape file
    cmdString = "aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -nc"         #check the effect of -nc
    #-o "\ +input_outletshp
    retDictionary = call_subprocess(cmdString, 'd8 contributing area')
    if retDictionary['success']=="False":
        return retDictionary
    #Get statistics of ad8 file to determine threshold

    #Stream definition by threshold
    cmdString = "threshold -ssa "+input_raster+"ad8.tif -src "+input_raster+"src.tif -thresh "+str(streamThreshold)
    retDictionary = call_subprocess(cmdString, 'Stream definition by threshold')
    if retDictionary['success']=="False":
        return retDictionary

    #move outlets to stream
    cmdString = "moveoutletstostrm -p "+input_raster+"p.tif -src "+input_raster+"src.tif -o "\
                +input_Outlet_shpFile+ " -om "+output_Outlet_shpFile
    retDictionary = call_subprocess(cmdString, 'move outlet to stream')
    if retDictionary['success']=="False":
        return retDictionary
    #Add projection to moved outlet ---TauDEM excludes the projection from moved outlet; check
    #project_Shapefile_UTM_NAD83("outletMoved.shp", output_Outlet_shpFile, utmZone)
    #driver = ogr.GetDriverByName("ESRI Shapefile")
    #dataset = driver.Open(input_Outlet_shpFile)
    #layer = dataset.GetLayer()
    #srs = layer.GetSpatialRef()
    baseName = os.path.splitext(output_Outlet_shpFile)[0]
    projFile = baseName+".prj"
    srsString = "+proj=utm +zone="+str(utmZone)+" +ellps=GRS80 +datum=NAD83 +units=m"
    srs = osr.SpatialReference()
    #srs.ImportFromEPSG(4326)
    srs.ImportFromProj4(srsString)
    srs.MorphFromESRI()
    file = open(projFile, "w")
    file.write(srs.ExportToWkt())
    file.close()
    #d8 contributing area with outlet shapefile
    cmdString = "aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -o "+output_Outlet_shpFile+" -nc"
    retDictionary = call_subprocess(cmdString, 'd8 contributing area with outlet shapefile')
    if retDictionary['success']=="False":
        return retDictionary
    #watershed grid file
    cmdString = "gdal_calc.py -A "+input_raster+"ad8.tif --outfile="+output_WS_raster+" --calc=A/A"
    retDictionary = call_subprocess(cmdString, "watershed grid computation")

    return retDictionary
    #To do: Delete temp raster
    #       Free other objects
    #       Direct TauDEM messages to file


def combineRasters(input_raster1=None, input_raster2=None, output_raster=None):
    """To  Do: may need to specify output no-data value
    """
    cmdString = "gdalwarp "+input_raster1+" "+input_raster2+" "+output_raster
    return call_subprocess(cmdString, 'join (stitch) two raster files')


def uncompressRaster(input_raster, output_raster):
    """TauDEM doesn't take compressed file; uncompress file
        ToDO:  Check compression first"""
    cmdString = "gdal_translate -co COMPRESS=NONE"+" "\
               +input_raster+" "+output_raster
    return call_subprocess(cmdString, 'uncompress raster')


def computeRasterAspect(input_raster=None, output_raster=None):
    cmdString = "gdaldem"+" "+"aspect"+" "+input_raster+" "+output_raster+" "+"-compute_edges"+" "+"-zero_for_flat"
    return call_subprocess(cmdString, 'compute aspect')


def computeRasterSlope(input_raster=None, output_raster=None):
    """ to run this from a different directory than the python module resides
    add path info: os.path......"""
    cmdString = "gdaldem"+" "+"slope"+" "+input_raster+" "+output_raster+" "+"-compute_edges"
    return call_subprocess(cmdString,'compute slope')


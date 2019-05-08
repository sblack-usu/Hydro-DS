__author__ = 'tsega'
#from hydrods_python_client import HydroDS
from hydrods_python_client_unified import HydroDS
import settings
from datetime import datetime, timedelta
"""*********** Input settings for watershed of interest *****************"""
workingDir = "/workDir/HydroDSTest/"

# Green River near Daniel at Warren Bridge
#leftX, topY, rightX, bottomY =  -110.415, 43.593, -109.492, 42.871
#Logan River above First Dam
leftX, topY, rightX, bottomY = -111.8037, 42.1248, -111.4255, 41.6946

#Green River near Daniel at Warren Bridge
#lat_outlet, lon_outlet = 4763468.844081, 572625.265184
#lat_outlet, lon_outlet = 43.019338, -110.118234
# Logan outlet at First dam
lat_outlet, lon_outlet = 41.7436,  -111.7838        #Logan

# Grid projection
#utmZone = int((180 + 0.5*(xmin+xmax))/6) + 1
epsgCode = 26912        #4326     #    #26912                 #26912 utm 12
dx,dy  = 30, 30  #  Grid cell sizes (m) for reprojection
# Set parameters for watershed delineation
streamThreshold = 300
watershedName = 'LoganT'
# Cell spacing for subsampled UEB model (m)
dxRes, dyRes = 800, 800
#### model start and end dates

#startDateTime = "2010/10/01 0"
#endDateTime = "2011/10/01 0"
startDateTime = "2008/10/01 0"
endDateTime = "2009/10/01 0"

inTime = 'time'
"""*************************************************************************"""
HDS = HydroDS(username=settings.USER_NAME, password=settings.PASSWORD)

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

## Test TOPNET

demUrl = 'http://hydro-ds.uwrl.usu.edu/files/data/user_5/GreenDEM84.tif'
outShpGrn = 'http://hydro-ds.uwrl.usu.edu/files/data/user_5/GreenmovOutlet.zip'

demRes = 'http://hydro-ds.uwrl.usu.edu/files/data/user_5/JLoganProj30.tif'  #'http://hydro-ds.uwrl.usu.edu/files/data/user_5/LoganProj50.tif'
outShp = 'http://hydro-ds.uwrl.usu.edu/files/data/user_5/JLoganmovOutlet.zip'

wsRequest = HDS.delineate_watershed_peuker_douglas(input_raster_url_path=demRes, threshold=300, peuker_min_threshold=5, peuker_max_threshold=500, peuker_number_threshold=10,
                    output_watershed_raster = "pgLogWS.tif",
                    output_outlet_shapefile = "pgLogWS.shp",
                    output_treefile = "pgLogTree.txt", output_coordfile = "pgLogCor.txt", output_streamnetfile = "pgLogNet.shp",
                    output_slopearea_raster = "pgLogSA.tif", output_distance_raster = "pgLogDist.tif",
                    input_outlet_shapefile_url_path = outShp,
           epsg_code=epsgCode, outlet_point_x=lon_outlet, outlet_point_y=lat_outlet)

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

#stream_request = HDS.download_streamflow(usgs_gage="", start_year=2009, end_year=2010,output_streamflow="Logan0910.dat")

#HDS.download_file(file_url_path=stream_request['output_streamflow'], save_as=workingDir+"Logan0910.dat")

print('Done')




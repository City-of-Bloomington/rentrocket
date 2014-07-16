-- You will probably need to put the txt files into /tmp
-- This might be the only directory MySQL is allowed to read from
--
-- Character Set:
-- The data files are most likely ANSI format.  You might need to convert
-- them to UTF8 before importing into MySQL
load data infile '/tmp/MonroeWebExport/ImprvList.txt'          into table ImprvList
load data infile '/tmp/MonroeWebExport/LandDescList.txt'       into table LandDescList
load data infile '/tmp/MonroeWebExport/Misc.txt'               into table Misc
load data infile '/tmp/MonroeWebExport/OtherPlumbingList.txt'  into table OtherPlumbingList
load data infile '/tmp/MonroeWebExport/ParcelGenInfo.txt'      into table ParcelGenInfo
load data infile '/tmp/MonroeWebExport/Photos.txt'             into table Photos
load data infile '/tmp/MonroeWebExport/PlumbingList.txt'       into table PlumbingList
load data infile '/tmp/MonroeWebExport/ResDetail.txt'          into table ResDetail
load data infile '/tmp/MonroeWebExport/ResFloor.txt'           into table ResFloor
load data infile '/tmp/MonroeWebExport/SalesList.txt'          into table SalesList
load data infile '/tmp/MonroeWebExport/SiteDescList.txt'       into table SiteDescList
load data infile '/tmp/MonroeWebExport/SketchList.txt'         into table SketchList
load data infile '/tmp/MonroeWebExport/SpecialFeatList.txt'    into table SpecialFeatList
load data infile '/tmp/MonroeWebExport/Streets.txt'            into table Streets
load data infile '/tmp/MonroeWebExport/tblDistricts.txt'       into table tblDistricts
load data infile '/tmp/MonroeWebExport/tblNeighborhoods.txt'   into table tblNeighborhoods
load data infile '/tmp/MonroeWebExport/tblTownshipNumbers.txt' into table tblTownshipNumbers
load data infile '/tmp/MonroeWebExport/Topo.txt'               into table Topo
load data infile '/tmp/MonroeWebExport/TransferOwnList.txt'    into table TransferOwnList
load data infile '/tmp/MonroeWebExport/Utility.txt'            into table Utility
load data infile '/tmp/MonroeWebExport/ValuationList.txt'      into table ValuationList
load data infile '/tmp/MonroeWebExport/WallTypeList.txt'       into table WallTypeList
load data infile '/tmp/MonroeWebExport/ServerLogType.txt'      into table ServerLogType
load data infile '/tmp/MonroeWebExport/ServerLog.txt'          into table ServerLog
load data infile '/tmp/MonroeWebExport/ImprvTypes.txt'         into table ImprvTypes
load data infile '/tmp/MonroeWebExport/DataDate.txt'           into table DataDate
load data infile '/tmp/MonroeWebExport/ExtFeatureList.txt'     into table ExtFeatureList
load data infile '/tmp/MonroeWebExport/FloorList.txt'          into table FloorList

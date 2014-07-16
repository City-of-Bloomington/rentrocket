-- You will probably need to put the txt files into /tmp
-- This might be the only directory MySQL is allowed to read from
--
-- Character Set:
-- The data files are most likely ANSI format.  You might need to convert
-- them to UTF8 before importing into MySQL
load data infile '/tmp/MonroeWebExport/ImprvList.txt'          into table ImprvList           fields terminated by '|';
load data infile '/tmp/MonroeWebExport/LandDescList.txt'       into table LandDescList        fields terminated by '|';
load data infile '/tmp/MonroeWebExport/Misc.txt'               into table Misc                fields terminated by '|';
load data infile '/tmp/MonroeWebExport/OtherPlumbingList.txt'  into table OtherPlumbingList   fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ParcelGenInfo.txt'      into table ParcelGenInfo       fields terminated by '|';
load data infile '/tmp/MonroeWebExport/Photos.txt'             into table Photos              fields terminated by '|';
load data infile '/tmp/MonroeWebExport/PlumbingList.txt'       into table PlumbingList        fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ResDetail.txt'          into table ResDetail           fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ResFloor.txt'           into table ResFloor            fields terminated by '|';
load data infile '/tmp/MonroeWebExport/SalesList.txt'          into table SalesList           fields terminated by '|';
load data infile '/tmp/MonroeWebExport/SiteDescList.txt'       into table SiteDescList        fields terminated by '|';
load data infile '/tmp/MonroeWebExport/SketchList.txt'         into table SketchList          fields terminated by '|';
load data infile '/tmp/MonroeWebExport/SpecialFeatList.txt'    into table SpecialFeatList     fields terminated by '|';
load data infile '/tmp/MonroeWebExport/Streets.txt'            into table Streets             fields terminated by '|';
load data infile '/tmp/MonroeWebExport/tblDistricts.txt'       into table tblDistricts        fields terminated by '|';
load data infile '/tmp/MonroeWebExport/tblNeighborhoods.txt'   into table tblNeighborhoods    fields terminated by '|';
load data infile '/tmp/MonroeWebExport/tblTownshipNumbers.txt' into table tblTownshipNumbers  fields terminated by '|';
load data infile '/tmp/MonroeWebExport/Topo.txt'               into table Topo                fields terminated by '|';
load data infile '/tmp/MonroeWebExport/TransferOwnList.txt'    into table TransferOwnList     fields terminated by '|';
load data infile '/tmp/MonroeWebExport/Utility.txt'            into table Utility             fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ValuationList.txt'      into table ValuationList       fields terminated by '|';
load data infile '/tmp/MonroeWebExport/WallTypeList.txt'       into table WallTypeList        fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ServerLogType.txt'      into table ServerLogType       fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ServerLog.txt'          into table ServerLog           fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ImprvTypes.txt'         into table ImprvTypes          fields terminated by '|';
load data infile '/tmp/MonroeWebExport/DataDate.txt'           into table DataDate            fields terminated by '|';
load data infile '/tmp/MonroeWebExport/ExtFeatureList.txt'     into table ExtFeatureList      fields terminated by '|';
load data infile '/tmp/MonroeWebExport/FloorList.txt'          into table FloorList           fields terminated by '|';

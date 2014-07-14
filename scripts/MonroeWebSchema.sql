create table tblTownshipNumbers(
	TownshipNumberID int unsigned not null primary key auto_increment,
	AreaNumber varchar(14) not null,
	TownshipName varchar(80) not null
);

create table tblNeighborhoods(
	NeighborhoodID int unsigned not null primary key auto_increment,
	Neighborhood varchar(14) not null,
	neigh_name varchar(80)
);

create table tblDistricts(
	DistrictID int unsigned not null primary key auto_increment,
	LocalDistrictNumber varchar(5),
	StateDistrictNumber varchar(5),
	DistrictName varchar(50) not null
);

create table ParcelGenInfo(
	ParcelKey int unsigned not null primary key auto_increment,
	Num                varchar(30),
	AltNum             varchar(30),
	TaxID              varchar(25),
	RoutingNbr         varchar(25),
	SectionPlat        varchar(8),
	ZoningCode         varchar(50),
	Subdivision        varchar(50),
	SubdivisionLot     varchar(15),
	StreetAddress      varchar(50),
	City               varchar(30),
	State              varchar(30),
	Zip                varchar(10),
	NeighborhoodName   varchar(80),
	NeighborhoodNumber varchar(14),
	NeighborhoodFactor       decimal(3, 2),
	PropertyClassNum   varchar(5),
	PropertyClassDesc  varchar(200),
	LegalDesc          text,
	OwnerName          varchar(50),
	OwnerName2         varchar(50),
	OwnerAddress       varchar(50),
	OwnerAddress2      varchar(50),
	OwnerCity          varchar(30),
	OwnerState         varchar(30),
	OwnerZip           varchar(10),
	TownshipName       varchar(50),
	TownshipNum        varchar(4),
	TaxDistrictNum     varchar(5),
	TaxDistrictName    varchar(50),
	SchoolCorp         varchar(50),
	TotalAcreage             decimal(18, 3),
	MarketAreaName     varchar(80),
	CalculatedAcreage        decimal(38, 6),
	CalculatedAcreageMinus82 decimal(38, 6),
	Lat    float,
	`Long` float
);

create table ImprvTypes(
	ImprvTypeID int unsigned not null primary key auto_increment,
	ImprvType varchar(255) not null
);

create table ImprvList(
	ImprvListID int unsigned not null primary key auto_increment,
	ParcelKey   int unsigned,
	Bldgs varchar(100) not null,
	Grade varchar(5),
	YrConst decimal(4, 0),
	EffYear decimal(4, 0),
	Cond varchar(5),
	Size int unsigned,
	ImprvTypeID int unsigned not null,
	PercentComplete decimal(3, 0),
	NbrhdFactor decimal(3, 2),
	MarketFactor decimal(5, 3),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey),
	foreign key (ImprvTypeID) references ImprvTypes(ImprvTypeID)
);


create table SalesList(
	SalesListID int unsigned not null primary key auto_increment,
	ParcelKey   int unsigned,
	PropertyClassCode varchar(5),
	ParcelAcreage decimal(10, 3),
	LandAV int,
	ImprAV int,
	TotalAV int,
	NeighborhoodCode varchar(14),
	NeighborhoodName varchar(80),
	`Date` datetime,
	Price decimal(18, 2),
	Buyer1Name varchar(100),
	Buyer1Address varchar(50),
	Buyer1City varchar(50),
	Buyer1State varchar(50),
	Buyer1Zip varchar(50),
	Buyer2Name varchar(100),
	Buyer2Address varchar(50),
	Buyer2City varchar(50),
	Buyer2State varchar(50),
	Buyer2Zip varchar(50),
	Seller1Name varchar(100),
	Seller1Address varchar(50),
	Seller1City varchar(50),
	Seller1State varchar(50),
	Seller1Zip varchar(50),
	Seller2Name varchar(100),
	Seller2Address varchar(50),
	Seller2City varchar(50),
	Seller2State varchar(50),
	Seller2Zip varchar(50),
	ParcelCount int,
	Valid varchar(1) not null,
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table ResFloor(
	ResFloorID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned,
	`Floor` varchar(3) not null,
	Construction varchar(50),
	BaseArea int,
	Finished int,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table ResDetail(
	ResDetailID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	StoryHeight decimal(4, 2),
	FinishedArea int,
	Fireplace int,
	HeatType varchar(50),
	NoHeating int,
	NoElectric int,
	AirCond int,
	IntegralGarages int,
	AttGarages int,
	AttCarports int,
	BsmtGarages int,
	Bedrooms int,
	FamilyRooms int,
	LivingRooms int,
	DiningRooms int,
	FinishedRooms int,
	FullBaths int,
	FullBathsFixtures int,
	HalfBaths int,
	HalfBathsFixtures int,
	HotWaterHeaters int,
	KitchenSinks int,
	AddFixtures int,
	BathTubswJets int not null,
	HotTubs int not null,
	BathTubswSteam int not null,
	Saunas int not null,
	SteamBaths int not null,
	Whirlpools int not null,
	OverallConstruction varchar(50),
	Style varchar(50),
	Rec1Area int,
	Rec2Area int,
	Rec3Area int,
	Rec4Area int,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table PlumbingList(
	PlumbingListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	ResNum int,
	ResFixtures int,
	CommNum int not null,
	CommFixtures int not null,
	ResFull int,
	ResHalf int,
	ResKitchen int,
	ResWaterHeater int,
	ResExtra int,
	CommFull int not null,
	CommHalf int not null,
	CommKitchen int not null,
	CommWaterHeater int not null,
	CommExtra int not null,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table Photos(
	PhotoListID int unsigned not null,
	ParcelKey int unsigned not null,
	FilePath varchar(1000),
	PrimaryPhoto int not null,
	primary key (PhotoListID, ParcelKey),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);


create table OtherPlumbingList(
	OtherPlumbingListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	GangSinks int,
	WashFountains int not null,
	DrinkingFountains int,
	WaterCoolerRefrig int,
	WaterCoolerHotCold int,
	ShowerUnits int,
	MultiStallShowers int,
	EmergEyeWashFount int,
	EmergShowers int,
	ShowerHeads int,
	BathTubswSteam int,
	Sauna int,
	NumSteamBaths int,
	Whirlpools int,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table Misc(
	MiscListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	Fireplaces int,
	IntegralGarages int not null,
	AttachedGarages int not null,
	AttachedCarports int not null,
	BasementGarages int not null,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table LandDescList(
	LandDescListID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	LandType varchar(4) not null,
	PricingMethod char(1),
	Dimensions varchar(100),
	Soil varchar(6),
	ActualFrontage int unsigned,
	EffectiveDepth decimal(4, 0),
	Factor decimal(18, 2),
	BaseRate decimal(19, 9),
	TotalValue decimal(18, 2),
	AdjustedRate decimal(36, 9),
	ExtendedValue decimal(38, 6),
	TotalInfluence decimal(38, 0),
	Cap1 decimal(5, 2),
	Cap2 decimal(5, 2),
	Cap3 decimal(5, 2),
	MarketFactor decimal(6, 4),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table FloorList(
	FloorListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned,
	FloorNum int not null,
	`Usage` varchar(50),
	UseArea int,
	NotinUse int,
	HeatingArea int,
	ACArea int,
	SprinkledArea int,
	SortOrder int,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table ExtFeatureList(
	ExtFeatureListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	Features varchar(100),
	Area int unsigned,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table SpecialFeatList(
	SpecialFeatListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	Description varchar(100),
	SizeQty int unsigned,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table SketchList(
	SketchListID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	FilePath varchar(200),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table SiteDescList(
	SiteDescList int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	Improving varchar(1) not null,
	Declining varchar(1) not null,
	Blighted varchar(1) not null,
	Static varchar(1) not null,
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table WallTypeList(
	WallTypeListID int unsigned not null primary key auto_increment,
	ImprvListID int unsigned not null,
	`Floor` int not null,
	WallType0 int,
	WallType1 int,
	WallType2 int,
	WallType3 int,
	WallType4 int,
	SortOrder int,
	foreign key (ImprvListID) references ImprvList(ImprvListID)
);

create table ValuationList(
	ValuationID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	AssessmentYear decimal(4, 0) not null,
	ReasonForChange varchar(45),
	LandValue int not null,
	ImprovValue int not null,
	TotalValue int not null,
	Cap1Land int,
	Cap1Improv int,
	Cap1Total int,
	Cap2Land int,
	Cap2AGLand int,
	Cap2LTCLand int,
	Cap2Improv int,
	Cap2LTCImp int,
	Cap2Total int,
	Cap3Land int,
	Cap3Improv int,
	Cap3Total int,
	ValuationDate datetime not null,
	ValuationMethod varchar(50),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table Topo(
	Topo_ID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	Flat varchar(1) not null,
	High varchar(1) not null,
	Low varchar(1) not null,
	Rolling varchar(1) not null,
	Swampy varchar(1) not null,
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table Utility(
	Topo_ID int unsigned not null primary key,
	ParcelKey int unsigned not null,
	Water varchar(1) not null,
	Sewer varchar(1) not null,
	Gas varchar(1) not null,
	Electricity varchar(1) not null,
	All_Utils varchar(1) not null,
	foreign key (Topo_ID) references Topo(Topo_ID),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table TransferOwnList(
	TransferOwnListID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	`Date` datetime not null,
	Name varchar(50),
	Book varchar(10),
	Page varchar(10),
	DocumentID varchar(20),
	SaleAmount int,
	DocumentCode varchar(5),
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table Streets(
	Streets_ID int unsigned not null primary key auto_increment,
	ParcelKey int unsigned not null,
	Sidewalk varchar(1) not null,
	Alley varchar(1) not null,
	Paved varchar(1) not null,
	Unpaved varchar(1) not null,
	Proposed varchar(1) not null,
	foreign key (ParcelKey) references ParcelGenInfo(ParcelKey)
);

create table DataDate(
	DataDate datetime
);

create table ServerLogType(
	LogTypeID int unsigned not null primary key auto_increment,
	Name varchar(20) not null
);

CREATE TABLE DimDate (
    DateKey       NVARCHAR(100) PRIMARY KEY,
    Year          INT NOT NULL,
    Month         INT ,
    Day           INT,
    Season        NVARCHAR(20)
);
GO
CREATE TABLE DimArtistGeography (
    GeoKey     NVARCHAR(100) PRIMARY KEY,
    BirthPlace NVARCHAR(200),
    Province   NVARCHAR(200),
    Region     NVARCHAR(200),
    Country    NVARCHAR(200),
    Latitude   FLOAT,
    Longitude  FLOAT
);
GO
CREATE TABLE DimArtist (
    ArtistKey     NVARCHAR(100) PRIMARY KEY,
    Name          NVARCHAR(200),
    Gender NVARCHAR(50)
        CHECK (Gender IN ('M', 'F') OR Gender IS NULL), 
    BirthDate     NVARCHAR(20),
    Nationality   NVARCHAR(200),
    Description   NVARCHAR(MAX),
    ActiveStart   NVARCHAR(20),
    ActiveEnd     NVARCHAR(20),
    Type          NVARCHAR(50),
    GeoKey        NVARCHAR(100) NOT NULL,

    FOREIGN KEY (GeoKey) REFERENCES DimArtistGeography(GeoKey)
);
GO
CREATE TABLE DimAlbum (
    AlbumKey     NVARCHAR(100) PRIMARY KEY,
    AlbumName    NVARCHAR(500),
    ReleaseDate  NVARCHAR(20),
    AlbumType    NVARCHAR(100)
);
GO
CREATE TABLE DimLyrics (
    LyricsKey            NVARCHAR(100) PRIMARY KEY,
    Language             NVARCHAR(20),
    Swear_IT             INT,
    Swear_EN             INT,
    Swear_IT_Words       NVARCHAR(MAX),
    Swear_EN_Words       NVARCHAR(MAX),
    NSentences           INT,
    NTokens              INT,
    CharPerToken         FLOAT,
    AvgTokenPerClause    FLOAT,
    Explicit             BIT,
    LyricsText           NVARCHAR(MAX)
);
GO
CREATE TABLE DimSymphony (
    SymphonyKey          NVARCHAR(100) PRIMARY KEY,
    BPM                  FLOAT,
    Rolloff              FLOAT,
    Flux                 FLOAT,
    RMS                  FLOAT,
    Flatness             FLOAT,
    SpectralComplexity   FLOAT,
    Pitch                FLOAT,
    Loudness             FLOAT
);
GO
CREATE TABLE DimSong (
    SongKey         NVARCHAR(100) PRIMARY KEY,
    Title           NVARCHAR(500),
    DiscNumber      INT,
    TrackNumber     INT,
    DurationMs      INT,
    Popularity      FLOAT,
    FeaturingArtists NVARCHAR(500),
	Category        NVARCHAR(100),
    AlbumKey        NVARCHAR(100),
    LyricsKey       NVARCHAR(100),
    SymphonyKey     NVARCHAR(100),
    

    FOREIGN KEY (AlbumKey) REFERENCES DimAlbum(AlbumKey),
    FOREIGN KEY (LyricsKey) REFERENCES DimLyrics(LyricsKey),
    FOREIGN KEY (SymphonyKey) REFERENCES DimSymphony(SymphonyKey)
);
GO
CREATE TABLE FactParticipation (
    SongKey        NVARCHAR(100) NOT NULL,
    ArtistKey      NVARCHAR(100) NOT NULL,
    DateKey        NVARCHAR(100) NOT NULL,
    Streams1Month  FLOAT,
    IsPrimary      BIT,

    FOREIGN KEY (SongKey) REFERENCES DimSong(SongKey),
    FOREIGN KEY (ArtistKey) REFERENCES DimArtist(ArtistKey),
    FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey)
);
GO


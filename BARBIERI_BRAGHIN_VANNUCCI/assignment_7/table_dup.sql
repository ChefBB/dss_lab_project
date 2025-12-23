USE Group_ID_8_DB;
GO

SELECT *
INTO Group_ID_8.DimAlbum_SSIS
FROM Group_ID_8.DimAlbum
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimArtist_SSIS
FROM Group_ID_8.DimArtist
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimArtistGeography_SSIS
FROM Group_ID_8.DimArtistGeography
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimDate_SSIS
FROM Group_ID_8.DimDate
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimLyrics_SSIS
FROM Group_ID_8.DimLyrics
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimSong_SSIS
FROM Group_ID_8.DimSong
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.DimSymphony_SSIS
FROM Group_ID_8.DimSymphony
WHERE 1 = 0;

SELECT *
INTO Group_ID_8.FactParticipation_SSIS
FROM Group_ID_8.FactParticipation
WHERE 1 = 0;
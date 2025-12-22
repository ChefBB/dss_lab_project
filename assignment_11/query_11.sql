
WITH FirstPublishedSong AS (
    SELECT
        FP.ArtistKey,
        FP.SongKey,
        FP.Streams1Month,
        ROW_NUMBER() OVER (
            PARTITION BY FP.ArtistKey
            ORDER BY DD.Year, DD.Month, DD.Day
        ) AS Rn
    FROM FactParticipation FP
    JOIN DimDate DD ON FP.DateKey = DD.DateKey
    WHERE FP.IsPrimary = 1
),

ArtistStats AS (
    SELECT
        ArtistKey,
        COUNT(*) AS TotalSongs,
        AVG(Streams1Month) AS AvgStreams,
        STDEV(Streams1Month) AS StDevStreams
    FROM FactParticipation
    WHERE IsPrimary = 1
    GROUP BY ArtistKey
),

SongsForGlobalRef AS (
    SELECT FPS.Streams1Month
    FROM FirstPublishedSong FPS
    JOIN ArtistStats A ON FPS.ArtistKey = A.ArtistKey
    WHERE FPS.Rn = 1 AND A.TotalSongs > 1
),

GlobalRefs AS (
    SELECT
        AVG(Streams1Month) AS GlobalAvgStreams,
        NULLIF(STDEV(Streams1Month),0) AS GlobalStDevStreams
    FROM SongsForGlobalRef
),

MainSongClassification AS (
    SELECT
        FP.SongKey,
        FP.ArtistKey AS MainArtistKey,
        FP.Streams1Month,
        CASE
            WHEN A.TotalSongs > 1 THEN A.AvgStreams
            ELSE (SELECT GlobalAvgStreams FROM GlobalRefs)
        END AS RefAvg,
        CASE
            WHEN A.TotalSongs > 1 THEN COALESCE(NULLIF(A.StDevStreams,0), 99999999)
            ELSE COALESCE(NULLIF((SELECT GlobalStDevStreams FROM GlobalRefs),0),99999999)
        END AS RefStd
    FROM FactParticipation FP
    JOIN ArtistStats A ON FP.ArtistKey = A.ArtistKey
    WHERE FP.IsPrimary = 1
),

MainSongStatus AS (
    SELECT
        SongKey,
        MainArtistKey,

        CASE WHEN Streams1Month >= RefAvg + RefStd THEN 1 ELSE 0 END AS IsTrending,
        CASE WHEN Streams1Month <= RefAvg - RefStd THEN 1 ELSE 0 END AS IsFlopping
    FROM MainSongClassification
),
MainArtistFinal AS (
    SELECT
        FP.ArtistKey,
        A.Name AS ArtistName,
        'Main' AS Role,
        COUNT(*) AS TotalSongs,
        SUM(MS.IsTrending) AS NumTrendingSongs,
        SUM(MS.IsFlopping) AS NumFloppingSongs
    FROM FactParticipation FP
    JOIN MainSongStatus MS ON FP.SongKey = MS.SongKey
    JOIN DimArtist A ON FP.ArtistKey = A.ArtistKey
    WHERE FP.IsPrimary = 1
    GROUP BY FP.ArtistKey, A.Name
),

FeaturedArtistFinal AS (
    SELECT
        FP.ArtistKey,
        A.Name AS ArtistName,
        'Feat' AS Role,
        COUNT(*) AS TotalSongs,
        SUM(MS.IsTrending) AS NumTrendingSongs,  
        SUM(MS.IsFlopping) AS NumFloppingSongs
    FROM FactParticipation FP
    JOIN MainSongStatus MS ON FP.SongKey = MS.SongKey
    JOIN DimArtist A ON FP.ArtistKey = A.ArtistKey
    WHERE FP.IsPrimary = 0
    GROUP BY FP.ArtistKey, A.Name
)

SELECT
    ArtistKey,
    ArtistName,
    Role,
    TotalSongs,
    NumTrendingSongs,
    NumFloppingSongs,

    -- Trending Percentage
    CASE
        WHEN TotalSongs > 0 THEN CAST(NumTrendingSongs AS FLOAT) / TotalSongs
        ELSE 0
    END AS TrendingPercentage,

    -- Trending Factor
    CASE 
        WHEN (NumTrendingSongs + NumFloppingSongs) > 0
            THEN CAST(NumTrendingSongs - NumFloppingSongs AS FLOAT)
                 / (NumTrendingSongs + NumFloppingSongs)
        ELSE 0
    END AS TrendingFactor

FROM (
    SELECT * FROM MainArtistFinal
    UNION ALL
    SELECT * FROM FeaturedArtistFinal
) AS X

ORDER BY Role DESC, TrendingFactor DESC;
 
SELECT 
    geo.Region AS Region,

    CASE 
        WHEN SUM(CASE WHEN d.Season = 'Winter' THEN 1 ELSE 0 END) = 0 THEN NULL
        ELSE ROUND(
            SUM(CASE WHEN d.Season = 'Summer' THEN 1 ELSE 0 END) * 1.0 /
            SUM(CASE WHEN d.Season = 'Winter' THEN 1 ELSE 0 END),
            3
        )
    END AS SummerWinterScore_Songs,

    CASE 
        WHEN SUM(CASE WHEN d.Season = 'Winter' THEN f.Streams1Month ELSE 0 END) = 0 THEN NULL
        ELSE ROUND(
            SUM(CASE WHEN d.Season = 'Summer' THEN f.Streams1Month END) * 1.0 /
            SUM(CASE WHEN d.Season = 'Winter' THEN f.Streams1Month END),
            3
        )
    END AS SummerWinterScore_Streams

FROM FactParticipation f
JOIN DimDate d 
    ON f.DateKey = d.DateKey
JOIN DimArtist a 
    ON f.ArtistKey = a.ArtistKey
JOIN DimArtistGeography geo 
    ON a.GeoKey = geo.GeoKey

WHERE 
    f.IsPrimary = 1
    AND d.Season IN ('Summer', 'Winter')

GROUP BY 
    geo.Region

ORDER BY 
    geo.Region;

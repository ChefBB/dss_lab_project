SELECT d.Year AS Year, a.Name AS Artist, COUNT(*) AS TotalSongs
FROM FactParticipation f 
JOIN DimDate d ON f.DateKey=d.DateKey
JOIN DimArtist a ON f.ArtistKey=a.ArtistKey
WHERE f.IsPrimary=1 
GROUP BY d.Year, a.Name
ORDER BY d.Year ASC, TotalSongs DESC, a.Name ASC 
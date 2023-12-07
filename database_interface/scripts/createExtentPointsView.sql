DROP VIEW IF EXISTS extent_sites CASCADE;
CREATE VIEW extent_sites AS
	SELECT
	her_geom.her_maphsa_id, her_geom.wkb_geometry
	FROM her_geom, extent
	WHERE st_intersects(her_geom.wkb_geometry, extent.geom)
;
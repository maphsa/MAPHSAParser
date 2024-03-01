-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2024-02-29 14:45:41.531

-- tables
-- Table: arch_ass
CREATE TABLE arch_ass (
    id serial  NOT NULL,
    her_maphsa_id int  NOT NULL,
    prev_res_act int  NOT NULL,
    her_morph int  NOT NULL,
    her_shape int  NOT NULL,
    her_loc_orient int  NOT NULL,
    o_arch_cert int  NOT NULL,
    CONSTRAINT arch_ass_pk PRIMARY KEY (id)
);

-- Table: built_comp
CREATE TABLE built_comp (
    id serial  NOT NULL,
    comp_mat int  NULL,
    comp_const_tech int  NULL,
    her_maphsa_id int  NOT NULL,
    comp_type int  NOT NULL,
    CONSTRAINT built_comp_pk PRIMARY KEY (id)
);

-- Table: built_comp_meas
CREATE TABLE built_comp_meas (
    id serial  NOT NULL,
    comp_dimen int  NOT NULL,
    comp_meas_unit int  NOT NULL,
    comp_meas_value real  NOT NULL,
    comp_meas_type int  NOT NULL,
    built_comp_id int  NOT NULL,
    CONSTRAINT built_comp_meas_pk PRIMARY KEY (id)
);

-- Table: cl_to_con
CREATE TABLE cl_to_con (
    id serial  NOT NULL,
    concept_list_concept_list_id int  NOT NULL,
    concept_table_concept_id int  NOT NULL,
    CONSTRAINT cl_to_con_pk PRIMARY KEY (id)
);

-- Table: concept_list
CREATE TABLE concept_list (
    concept_list_id serial  NOT NULL,
    concept_list_value varchar(128)  NOT NULL,
    CONSTRAINT concept_list_pk PRIMARY KEY (concept_list_id)
);

-- Table: concept_table
CREATE TABLE concept_table (
    concept_id serial  NOT NULL,
    concept_theme varchar(64)  NOT NULL,
    concept_string varchar(128)  NOT NULL,
    concept_descr varchar(756)  NOT NULL,
    concept_thesaurus_id int  NOT NULL,
    CONSTRAINT concept_table_pk PRIMARY KEY (concept_id)
);

-- Table: concept_thesaurus
CREATE TABLE concept_thesaurus (
    id serial  NOT NULL,
    name varchar(256)  NOT NULL,
    description varchar(512)  NOT NULL,
    CONSTRAINT concept_thesaurus_pk PRIMARY KEY (id)
);

-- Table: data_origin
CREATE TABLE data_origin (
    name varchar(128)  NOT NULL,
    meta_data jsonb  NOT NULL,
    CONSTRAINT id PRIMARY KEY (name)
);

-- Table: disturbance_event
CREATE TABLE disturbance_event (
    id serial  NOT NULL,
    dist_cause int  NOT NULL,
    dist_effect int  NOT NULL,
    dist_from interval  NULL,
    over_dam_ext int  NOT NULL,
    her_cond_ass_id int  NOT NULL,
    CONSTRAINT disturbance_event_pk PRIMARY KEY (id)
);

-- Table: elevation
CREATE TABLE elevation (
    id serial  NOT NULL,
    sp_coord int  NOT NULL,
    min_elev real  NOT NULL,
    max_elev real  NOT NULL,
    env_assessment_id int  NOT NULL,
    meas_type int  NOT NULL,
    CONSTRAINT elevation_pk PRIMARY KEY (id)
);

-- Table: env_assessment
CREATE TABLE env_assessment (
    id serial  NOT NULL,
    topo_type int  NOT NULL,
    lcov_type int  NOT NULL,
    bedr_geo int  NOT NULL,
    soil_class int  NOT NULL,
    l_use_type int  NOT NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT env_assessment_pk PRIMARY KEY (id)
);

-- Table: grid
CREATE TABLE grid (
    id serial  NOT NULL,
    grid_id varchar(100)  NOT NULL,
    CONSTRAINT grid_pk PRIMARY KEY (id)
);

-- Table: her_admin_div
CREATE TABLE her_admin_div (
    id serial  NOT NULL,
    admin_div_name varchar(100)  NULL,
    admin_type int  NOT NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT her_admin_div_pk PRIMARY KEY (id)
);

-- Table: her_cond_ass
CREATE TABLE her_cond_ass (
    id serial  NOT NULL,
    recc_type int  NOT NULL,
    cond_assessor varchar(100)  NOT NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT her_cond_ass_pk PRIMARY KEY (id)
);

-- Table: her_feature
CREATE TABLE her_feature (
    id serial  NOT NULL,
    feat_type int  NOT NULL,
    feat_count real  NOT NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT her_feature_pk PRIMARY KEY (id)
);

-- Table: her_find
CREATE TABLE her_find (
    id serial  NOT NULL,
    art_cat_concept_list_id int  NOT NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT her_find_pk PRIMARY KEY (id)
);

-- Table: her_geom
CREATE TABLE her_geom (
    id_loc_ serial  NOT NULL,
    loc_cert int  NOT NULL,
    geom_ext_ert int  NOT NULL,
    sys_ref int  NOT NULL,
    lat real  NOT NULL,
    long real  NOT NULL,
    her_maphsa_id int  NOT NULL,
    grid_id int  NOT NULL,
    CONSTRAINT her_geom_pk PRIMARY KEY (id_loc_)
);

SELECT AddGeometryColumn('public','her_geom','wkb_geometry',4326,'POINT',2);
SELECT AddGeometryColumn('public','her_geom','her_polygon',4326,'MULTIPOLYGON',2);;

-- Table: her_loc_funct
CREATE TABLE her_loc_funct (
    id serial  NOT NULL,
    her_loc_funct int  NOT NULL,
    her_loc_fun_cert int  NOT NULL,
    arch_ass_id int  NOT NULL,
    CONSTRAINT her_loc_funct_pk PRIMARY KEY (id)
);

-- Table: her_loc_meas
CREATE TABLE her_loc_meas (
    id serial  NOT NULL,
    her_dimen int  NOT NULL,
    her_meas_unit int  NOT NULL,
    her_meas_value real  NOT NULL,
    her_meas_type int  NOT NULL,
    arch_ass_id int  NOT NULL,
    CONSTRAINT her_loc_meas_pk PRIMARY KEY (id)
);

-- Table: her_loc_name
CREATE TABLE her_loc_name (
    id serial  NOT NULL,
    her_loc_name varchar(256)  NULL,
    her_loc_sum_id int  NOT NULL,
    her_loc_name_type int  NOT NULL,
    CONSTRAINT her_loc_name_pk PRIMARY KEY (id)
);

-- Table: her_loc_sum
CREATE TABLE her_loc_sum (
    id serial  NOT NULL,
    gen_descr varchar(500)  NULL,
    her_maphsa_id int  NOT NULL,
    CONSTRAINT her_loc_sum_pk PRIMARY KEY (id)
);

-- Table: her_loc_type
CREATE TABLE her_loc_type (
    id serial  NOT NULL,
    her_loc_type int  NOT NULL,
    her_loc_typcert int  NOT NULL,
    her_loc_sum_id int  NOT NULL,
    CONSTRAINT her_loc_type_pk PRIMARY KEY (id)
);

-- Table: her_maphsa
CREATE TABLE her_maphsa (
    id serial  NOT NULL,
    id_maphsa varchar(100)  NOT NULL,
    comment varchar(250)  NULL,
    her_source_id int  NOT NULL,
    information_resource_id int  NOT NULL,
    CONSTRAINT her_maphsa_pk PRIMARY KEY (id)
);

-- Table: her_source
CREATE TABLE her_source (
    id serial  NOT NULL,
    location varchar(128)  NOT NULL,
    data_origin_name varchar(128)  NOT NULL,
    CONSTRAINT her_source_pk PRIMARY KEY (id)
);

-- Table: hydro_info
CREATE TABLE hydro_info (
    id serial  NOT NULL,
    hydro_type int  NOT NULL,
    hydro_name varchar(150)  NOT NULL,
    env_assessment_id int  NOT NULL,
    CONSTRAINT hydro_info_pk PRIMARY KEY (id)
);

-- Table: information_resource
CREATE TABLE information_resource (
   id serial  NOT NULL,
   id_maphsa varchar(128)  NOT NULL,
   url varchar(128)  NULL,
   bib_title varchar(128)  NULL,
   bib_pub_date date  NULL,
   bib_edition varchar(128)  NULL,
   bib_issue varchar(128)  NULL,
   bib_journal varchar(128)  NULL,
   bib_pub_place varchar(128)  NULL,
   bib_publisher varchar(128)  NULL,
   bib_pages varchar(128)  NULL,
   description varchar(256)  NULL,
   inf_res_type int  NOT NULL,
   CONSTRAINT information_resource_pk PRIMARY KEY (id)
);

-- Table: information_resource_author
CREATE TABLE information_resource_author (
    id int  NOT NULL,
    author_appellation varchar(128)  NOT NULL,
    information_resource_id int  NOT NULL,
    CONSTRAINT information_resource_author_pk PRIMARY KEY (id)
);

-- Table: information_resource_editor
CREATE TABLE information_resource_editor (
    id int  NOT NULL,
    editor_apellation varchar(128)  NOT NULL,
    information_resource_id int  NOT NULL,
    CONSTRAINT information_resource_editor_pk PRIMARY KEY (id)
);

-- Table: land_own
CREATE TABLE land_own (
    id serial  NOT NULL,
    land_own_type int  NOT NULL,
    lev_prot int  NOT NULL,
    prot_fromdate varchar(100)  NOT NULL,
    prot_to varchar(100)  NOT NULL,
    env_assessment_id int  NOT NULL,
    CONSTRAINT land_own_pk PRIMARY KEY (id)
);

-- Table: pers_org_res_adm_div
CREATE TABLE pers_org_res_adm_div (
    pers_org_res_id int  NOT NULL,
    her_admin_div_id int  NOT NULL,
    CONSTRAINT pers_org_res_adm_div_pk PRIMARY KEY (her_admin_div_id,pers_org_res_id)
);

-- Table: person_organization_resource
CREATE TABLE person_organization_resource (
    id int  NOT NULL,
    ip_maphsa varchar(128)  NOT NULL,
    name varchar(128)  NOT NULL,
    place_address varchar(256)  NOT NULL,
    description varchar(256)  NOT NULL,
    person_organization_category int  NOT NULL,
    actor_role_type int  NOT NULL,
    actor_role_type_from date  NOT NULL,
    actor_role_type_to date  NOT NULL,
    CONSTRAINT person_organization_resource_pk PRIMARY KEY (id)
);

-- Table: risk_assessment
CREATE TABLE risk_assessment (
    id serial  NOT NULL,
    threat_type int  NOT NULL,
    threat_prob int  NOT NULL,
    her_cond_ass_id int  NOT NULL,
    CONSTRAINT risk_assessment_pk PRIMARY KEY (id)
);

-- Table: site_cult_aff
CREATE TABLE site_cult_aff (
    id serial  NOT NULL,
    cult_aff int  NOT NULL,
    cult_aff_certainty int  NOT NULL,
    arch_ass_id int  NOT NULL,
    CONSTRAINT site_cult_aff_pk PRIMARY KEY (id)
);

-- Table: sites_timespace
CREATE TABLE sites_timespace (
    id serial  NOT NULL,
    to_date interval  NOT NULL,
    from_date interval  NOT NULL,
    period_cert int  NOT NULL,
    arch_ass_id int  NOT NULL,
    CONSTRAINT sites_timespace_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: actor_role_type (table: person_organization_resource)
ALTER TABLE person_organization_resource ADD CONSTRAINT actor_role_type
    FOREIGN KEY (actor_role_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: aher_loc_type_concept_table (table: her_loc_type)
ALTER TABLE her_loc_type ADD CONSTRAINT aher_loc_type_concept_table
    FOREIGN KEY (her_loc_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: arch_ass_concept_table (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT arch_ass_concept_table
    FOREIGN KEY (her_shape)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: arch_ass_her_maphsa (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT arch_ass_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: arch_cert_concept_table (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT arch_cert_concept_table
    FOREIGN KEY (o_arch_cert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: bedrock_concept_list (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT bedrock_concept_list
    FOREIGN KEY (bedr_geo)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: bher_loc_typecert_concept_table (table: her_loc_type)
ALTER TABLE her_loc_type ADD CONSTRAINT bher_loc_typecert_concept_table
    FOREIGN KEY (her_loc_typcert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: built_comp_concept_table (table: built_comp)
ALTER TABLE built_comp ADD CONSTRAINT built_comp_concept_table
    FOREIGN KEY (comp_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: built_comp_meas_built_comp (table: built_comp_meas)
ALTER TABLE built_comp_meas ADD CONSTRAINT built_comp_meas_built_comp
    FOREIGN KEY (built_comp_id)
    REFERENCES built_comp (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: c_meas_type_concept_table (table: built_comp_meas)
ALTER TABLE built_comp_meas ADD CONSTRAINT c_meas_type_concept_table
    FOREIGN KEY (comp_meas_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: c_meas_unit_concept_table (table: built_comp_meas)
ALTER TABLE built_comp_meas ADD CONSTRAINT c_meas_unit_concept_table
    FOREIGN KEY (comp_meas_unit)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: cl_to_con_concept_list (table: cl_to_con)
ALTER TABLE cl_to_con ADD CONSTRAINT cl_to_con_concept_list
    FOREIGN KEY (concept_list_concept_list_id)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: cl_to_con_concept_table (table: cl_to_con)
ALTER TABLE cl_to_con ADD CONSTRAINT cl_to_con_concept_table
    FOREIGN KEY (concept_table_concept_id)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: comp_dim_concept_table (table: built_comp_meas)
ALTER TABLE built_comp_meas ADD CONSTRAINT comp_dim_concept_table
    FOREIGN KEY (comp_dimen)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: comp_mat_concept_list (table: built_comp)
ALTER TABLE built_comp ADD CONSTRAINT comp_mat_concept_list
    FOREIGN KEY (comp_mat)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: concept_table_concept_thesaurus (table: concept_table)
ALTER TABLE concept_table ADD CONSTRAINT concept_table_concept_thesaurus
    FOREIGN KEY (concept_thesaurus_id)
    REFERENCES concept_thesaurus (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: constr_tech_concept_list (table: built_comp)
ALTER TABLE built_comp ADD CONSTRAINT constr_tech_concept_list
    FOREIGN KEY (comp_const_tech)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: cult_aff_cert_concept_table (table: site_cult_aff)
ALTER TABLE site_cult_aff ADD CONSTRAINT cult_aff_cert_concept_table
    FOREIGN KEY (cult_aff_certainty)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: cult_aff_concept_table (table: site_cult_aff)
ALTER TABLE site_cult_aff ADD CONSTRAINT cult_aff_concept_table
    FOREIGN KEY (cult_aff)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: dam_ass_concept_table (table: disturbance_event)
ALTER TABLE disturbance_event ADD CONSTRAINT dam_ass_concept_table
    FOREIGN KEY (over_dam_ext)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: dim_unit_concept_table (table: her_loc_meas)
ALTER TABLE her_loc_meas ADD CONSTRAINT dim_unit_concept_table
    FOREIGN KEY (her_meas_unit)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: dimension_concept_table (table: her_loc_meas)
ALTER TABLE her_loc_meas ADD CONSTRAINT dimension_concept_table
    FOREIGN KEY (her_dimen)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: dist_cause_concept_table (table: disturbance_event)
ALTER TABLE disturbance_event ADD CONSTRAINT dist_cause_concept_table
    FOREIGN KEY (dist_cause)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: dist_effect_concept_list (table: disturbance_event)
ALTER TABLE disturbance_event ADD CONSTRAINT dist_effect_concept_list
    FOREIGN KEY (dist_effect)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: disturbance_ass_her_cond_ass (table: disturbance_event)
ALTER TABLE disturbance_event ADD CONSTRAINT disturbance_ass_her_cond_ass
    FOREIGN KEY (her_cond_ass_id)
    REFERENCES her_cond_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: elevation_env_assessment (table: elevation)
ALTER TABLE elevation ADD CONSTRAINT elevation_env_assessment
    FOREIGN KEY (env_assessment_id)
    REFERENCES env_assessment (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: env_assessment_her_maphsa (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT env_assessment_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: feat_type_concept_table (table: her_feature)
ALTER TABLE her_feature ADD CONSTRAINT feat_type_concept_table
    FOREIGN KEY (feat_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: geom_ex_concept_table (table: her_geom)
ALTER TABLE her_geom ADD CONSTRAINT geom_ex_concept_table
    FOREIGN KEY (geom_ext_ert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_admin_div_concept_table (table: her_admin_div)
ALTER TABLE her_admin_div ADD CONSTRAINT her_admin_div_concept_table
    FOREIGN KEY (admin_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_admin_div_her_maphsa (table: her_admin_div)
ALTER TABLE her_admin_div ADD CONSTRAINT her_admin_div_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_cond_ass_her_maphsa (table: her_cond_ass)
ALTER TABLE her_cond_ass ADD CONSTRAINT her_cond_ass_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_feature_her_maphsa (table: her_feature)
ALTER TABLE her_feature ADD CONSTRAINT her_feature_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_find_concept_list (table: her_find)
ALTER TABLE her_find ADD CONSTRAINT her_find_concept_list
    FOREIGN KEY (art_cat_concept_list_id)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_find_her_maphsa (table: her_find)
ALTER TABLE her_find ADD CONSTRAINT her_find_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_geom_grid (table: her_geom)
ALTER TABLE her_geom ADD CONSTRAINT her_geom_grid
    FOREIGN KEY (grid_id)
    REFERENCES grid (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_geom_her_maphsa (table: her_geom)
ALTER TABLE her_geom ADD CONSTRAINT her_geom_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_concept_table (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT her_loc_concept_table
    FOREIGN KEY (her_loc_orient)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_funccert_concept_table (table: her_loc_funct)
ALTER TABLE her_loc_funct ADD CONSTRAINT her_loc_funccert_concept_table
    FOREIGN KEY (her_loc_fun_cert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_funct_arch_ass (table: her_loc_funct)
ALTER TABLE her_loc_funct ADD CONSTRAINT her_loc_funct_arch_ass
    FOREIGN KEY (arch_ass_id)
    REFERENCES arch_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_funct_concept_table (table: her_loc_funct)
ALTER TABLE her_loc_funct ADD CONSTRAINT her_loc_funct_concept_table
    FOREIGN KEY (her_loc_funct)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_meas_arch_ass (table: her_loc_meas)
ALTER TABLE her_loc_meas ADD CONSTRAINT her_loc_meas_arch_ass
    FOREIGN KEY (arch_ass_id)
    REFERENCES arch_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_name_concept_table (table: her_loc_name)
ALTER TABLE her_loc_name ADD CONSTRAINT her_loc_name_concept_table
    FOREIGN KEY (her_loc_name_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_name_her_loc_sum (table: her_loc_name)
ALTER TABLE her_loc_name ADD CONSTRAINT her_loc_name_her_loc_sum
    FOREIGN KEY (her_loc_sum_id)
    REFERENCES her_loc_sum (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_sum_her_maphsa (table: her_loc_sum)
ALTER TABLE her_loc_sum ADD CONSTRAINT her_loc_sum_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_type_concept_table (table: her_loc_type)
ALTER TABLE her_loc_type ADD CONSTRAINT her_loc_type_concept_table
    FOREIGN KEY (her_loc_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_type_her_loc_sum (table: her_loc_type)
ALTER TABLE her_loc_type ADD CONSTRAINT her_loc_type_her_loc_sum
    FOREIGN KEY (her_loc_sum_id)
    REFERENCES her_loc_sum (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_loc_typecert_concept_table (table: her_loc_type)
ALTER TABLE her_loc_type ADD CONSTRAINT her_loc_typecert_concept_table
    FOREIGN KEY (her_loc_typcert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_maphsa_her_source (table: her_maphsa)
ALTER TABLE her_maphsa ADD CONSTRAINT her_maphsa_her_source
    FOREIGN KEY (her_source_id)
    REFERENCES her_source (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_maphsa_information_resource (table: her_maphsa)
ALTER TABLE her_maphsa ADD CONSTRAINT her_maphsa_information_resource
    FOREIGN KEY (information_resource_id)
    REFERENCES information_resource (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: her_source_data_origin (table: her_source)
ALTER TABLE her_source ADD CONSTRAINT her_source_data_origin
    FOREIGN KEY (data_origin_name)
    REFERENCES data_origin (name)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: hydro_info (table: hydro_info)
ALTER TABLE hydro_info ADD CONSTRAINT hydro_info
    FOREIGN KEY (env_assessment_id)
    REFERENCES env_assessment (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: hydro_type_concept_list (table: hydro_info)
ALTER TABLE hydro_info ADD CONSTRAINT hydro_type_concept_list
    FOREIGN KEY (hydro_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: information_resource_author_information_resource (table: information_resource_author)
ALTER TABLE information_resource_author ADD CONSTRAINT information_resource_author_information_resource
    FOREIGN KEY (information_resource_id)
    REFERENCES information_resource (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: information_resource_concept_table (table: information_resource)
ALTER TABLE information_resource ADD CONSTRAINT information_resource_concept_table
    FOREIGN KEY (inf_res_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: information_resource_editor_information_resource (table: information_resource_editor)
ALTER TABLE information_resource_editor ADD CONSTRAINT information_resource_editor_information_resource
    FOREIGN KEY (information_resource_id)
    REFERENCES information_resource (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: l_use_concept_list (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT l_use_concept_list
    FOREIGN KEY (l_use_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: land_own_concept_table (table: land_own)
ALTER TABLE land_own ADD CONSTRAINT land_own_concept_table
    FOREIGN KEY (land_own_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: land_own_env_assessment (table: land_own)
ALTER TABLE land_own ADD CONSTRAINT land_own_env_assessment
    FOREIGN KEY (env_assessment_id)
    REFERENCES env_assessment (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: lcover_concept_list (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT lcover_concept_list
    FOREIGN KEY (lcov_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: level_prot_concept_table (table: land_own)
ALTER TABLE land_own ADD CONSTRAINT level_prot_concept_table
    FOREIGN KEY (lev_prot)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: loc_cert_concept_table (table: her_geom)
ALTER TABLE her_geom ADD CONSTRAINT loc_cert_concept_table
    FOREIGN KEY (loc_cert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: meas_type_concept_table (table: elevation)
ALTER TABLE elevation ADD CONSTRAINT meas_type_concept_table
    FOREIGN KEY (meas_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: morphology_concept_table (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT morphology_concept_table
    FOREIGN KEY (her_morph)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: period_cert_concept_table (table: sites_timespace)
ALTER TABLE sites_timespace ADD CONSTRAINT period_cert_concept_table
    FOREIGN KEY (period_cert)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: pers_org_res_adm_div_pers_org_res (table: pers_org_res_adm_div)
ALTER TABLE pers_org_res_adm_div ADD CONSTRAINT pers_org_res_adm_div_pers_org_res
    FOREIGN KEY (pers_org_res_id)
    REFERENCES person_organization_resource (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: person_organization_resource_adm_div_her_admin_div (table: pers_org_res_adm_div)
ALTER TABLE pers_org_res_adm_div ADD CONSTRAINT person_organization_resource_adm_div_her_admin_div
    FOREIGN KEY (her_admin_div_id)
    REFERENCES her_admin_div (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: person_organization_resource_concept_table (table: person_organization_resource)
ALTER TABLE person_organization_resource ADD CONSTRAINT person_organization_resource_concept_table
    FOREIGN KEY (person_organization_category)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: prev_research_concept_list (table: arch_ass)
ALTER TABLE arch_ass ADD CONSTRAINT prev_research_concept_list
    FOREIGN KEY (prev_res_act)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: recc_type_concept_list (table: her_cond_ass)
ALTER TABLE her_cond_ass ADD CONSTRAINT recc_type_concept_list
    FOREIGN KEY (recc_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: s_meas_type_concept_table (table: her_loc_meas)
ALTER TABLE her_loc_meas ADD CONSTRAINT s_meas_type_concept_table
    FOREIGN KEY (her_meas_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: site_comp_her_maphsa (table: built_comp)
ALTER TABLE built_comp ADD CONSTRAINT site_comp_her_maphsa
    FOREIGN KEY (her_maphsa_id)
    REFERENCES her_maphsa (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: site_cult_aff_arch_ass (table: site_cult_aff)
ALTER TABLE site_cult_aff ADD CONSTRAINT site_cult_aff_arch_ass
    FOREIGN KEY (arch_ass_id)
    REFERENCES arch_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: sites_timespace_arch_ass (table: sites_timespace)
ALTER TABLE sites_timespace ADD CONSTRAINT sites_timespace_arch_ass
    FOREIGN KEY (arch_ass_id)
    REFERENCES arch_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: soil_concept_list (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT soil_concept_list
    FOREIGN KEY (soil_class)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: spat_coord_concept_table (table: elevation)
ALTER TABLE elevation ADD CONSTRAINT spat_coord_concept_table
    FOREIGN KEY (sp_coord)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: sys_ref_concept_table (table: her_geom)
ALTER TABLE her_geom ADD CONSTRAINT sys_ref_concept_table
    FOREIGN KEY (sys_ref)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: threat_assessment_her_cond_ass (table: risk_assessment)
ALTER TABLE risk_assessment ADD CONSTRAINT threat_assessment_her_cond_ass
    FOREIGN KEY (her_cond_ass_id)
    REFERENCES her_cond_ass (id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: threat_prob_concept_table (table: risk_assessment)
ALTER TABLE risk_assessment ADD CONSTRAINT threat_prob_concept_table
    FOREIGN KEY (threat_prob)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: threat_type_concept_table (table: risk_assessment)
ALTER TABLE risk_assessment ADD CONSTRAINT threat_type_concept_table
    FOREIGN KEY (threat_type)
    REFERENCES concept_table (concept_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- Reference: topogr_concept_list (table: env_assessment)
ALTER TABLE env_assessment ADD CONSTRAINT topogr_concept_list
    FOREIGN KEY (topo_type)
    REFERENCES concept_list (concept_list_id)
    NOT DEFERRABLE
    INITIALLY IMMEDIATE
;

-- End of file.


-- Data source master rows
INSERT INTO public.grid(id, grid_id) VALUES (DEFAULT, 'Placeholder grid');

INSERT INTO public.her_admin_div (id, admin_div_name, admin_type) VALUES
(DEFAULT, 'Brazil', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country')),
(DEFAULT, 'Colombia', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country')),
(DEFAULT, 'Spain', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country')),
(DEFAULT, 'Netherlands', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country')),
(DEFAULT, 'São Paulo', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'State')),
(DEFAULT, 'São Paulo', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')),
(DEFAULT, 'Catalunya', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region')),
(DEFAULT, 'Tarragona', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')),
(DEFAULT, 'Barcelona', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')),
(DEFAULT, 'South Holland', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Province')),
(DEFAULT, 'Leiden', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')),
(DEFAULT, 'Magdalena', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Department')),
(DEFAULT, 'Santa Marta', (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,'37326a62-699c-4a42-b7cf-eb0cb55e58f2','Universidade de São Paulo','Av. Prof. Almeida Prado, 1466 Cidade Universitária – São Paulo/SP 05508-070','Partner Institution',(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Organization'),(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),'2024-01-01 00:00:00.001','2025-12-31 23:59:59.001'),
(DEFAULT,'8d353cf3-71ee-4010-84b3-4aa26af85107','Universitat Pompeu Fabra','Ramon Trias Fargas 25-27 08005 Barcelona','Lead Institution',(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Organization'),(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'), '2024-01-01 00:00:00.001','2025-12-31 23:59:59.001'),
(DEFAULT,'d1895d4f-20d2-4521-8a48-65e6f02bcb9f','Institut Català d\'Arqueologia Clàssica','Plaça d\'en Rovellat, s/n, 43003 Tarragona','Partner Institution',(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Organization'),(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),'2024-01-01 00:00:00.001','2025-12-31 23:59:59.001'),
(DEFAULT,'35b321fa-8ee8-4176-abf2-bc184fb0806a','Universiteit Leiden','Snellius Niels Bohrweg 1 2333 CA Leiden','Partner Institution',(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Organization'), (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),'2024-01-01 00:00:00.001','2025-12-31 23:59:59.001'),
(DEFAULT,'2f33013f-9d7e-48a0-9768-a977020fcc23','Universidad del Magdalena','Carrera 32 No 22 - 08 Santa Marta D.T.C.H. - Colombia Código Postal No. 470004','Partner Institution',(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Organization'), (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),'2024-01-01 00:00:00.001','2025-12-31 23:59:59.001');

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'd4b74c02-0b17-48bb-a93f-744fa68d42a3',
'Rafael Cardoso de Almeida Lopes',
'Av. Prof. Almeida Prado, 1466 Cidade Universitária – São Paulo/SP 05508-070',
'Post-Doctoral Research Associate',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'd4b74c02-0b17-48bb-a93f-744fa68d42a3'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Brazil' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'd4b74c02-0b17-48bb-a93f-744fa68d42a3'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'State'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'd4b74c02-0b17-48bb-a93f-744fa68d42a3'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'd4b74c02-0b17-48bb-a93f-744fa68d42a3'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37326a62-699c-4a42-b7cf-eb0cb55e58f2'));


INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'32eb3833-08bc-46cf-91ad-c45240170573',
'Rodrigo Elias de Oliveira',
'Av. Prof. Almeida Prado, 1466 Cidade Universitária – São Paulo/SP 05508-070',
'Post-Doctoral Research Associate',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '32eb3833-08bc-46cf-91ad-c45240170573'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Brazil' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '32eb3833-08bc-46cf-91ad-c45240170573'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'State'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '32eb3833-08bc-46cf-91ad-c45240170573'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '32eb3833-08bc-46cf-91ad-c45240170573'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37326a62-699c-4a42-b7cf-eb0cb55e58f2'));


INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'9d203550-6cdf-4487-aa9f-6909579cf363',
'Eduardo Góes Neves',
'Av. Prof. Almeida Prado, 1466 Cidade Universitária – São Paulo/SP 05508-070',
'Co-Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '9d203550-6cdf-4487-aa9f-6909579cf363'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Brazil' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '9d203550-6cdf-4487-aa9f-6909579cf363'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'State'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '9d203550-6cdf-4487-aa9f-6909579cf363'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '9d203550-6cdf-4487-aa9f-6909579cf363'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37326a62-699c-4a42-b7cf-eb0cb55e58f2'));


INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'f86cea3b-2952-482b-85ee-9e580e97c66d',
'André Menezes Strauss',
'Av. Prof. Almeida Prado, 1466 Cidade Universitária – São Paulo/SP 05508-070',
'Co-Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'f86cea3b-2952-482b-85ee-9e580e97c66d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Brazil' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'f86cea3b-2952-482b-85ee-9e580e97c66d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'State'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'f86cea3b-2952-482b-85ee-9e580e97c66d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'São Paulo' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'f86cea3b-2952-482b-85ee-9e580e97c66d'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37326a62-699c-4a42-b7cf-eb0cb55e58f2'));


INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'15a5e289-1e58-48e0-bfc4-db40f4025e5d',
'Jonas Gregorio de Souza',
'Ramon Trias Fargas 25-27 08005 Barcelona',
'Project Manager',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '15a5e289-1e58-48e0-bfc4-db40f4025e5d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '15a5e289-1e58-48e0-bfc4-db40f4025e5d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '15a5e289-1e58-48e0-bfc4-db40f4025e5d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Barcelona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '15a5e289-1e58-48e0-bfc4-db40f4025e5d'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8d353cf3-71ee-4010-84b3-4aa26af85107'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'787d6732-2317-4b6c-95ed-1cee495f0eca',
'Alan Tapscott Baltar',
'Ramon Trias Fargas 25-27 08005 Barcelona',
'Database Manager',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '787d6732-2317-4b6c-95ed-1cee495f0eca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '787d6732-2317-4b6c-95ed-1cee495f0eca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '787d6732-2317-4b6c-95ed-1cee495f0eca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Barcelona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '787d6732-2317-4b6c-95ed-1cee495f0eca'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8d353cf3-71ee-4010-84b3-4aa26af85107'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'8ecfb716-0962-4564-bd40-894b7727e1ca',
'Marco Moderato',
'Ramon Trias Fargas 25-27 08005 Barcelona',
'Post-Doctoral Research Associate',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8ecfb716-0962-4564-bd40-894b7727e1ca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8ecfb716-0962-4564-bd40-894b7727e1ca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8ecfb716-0962-4564-bd40-894b7727e1ca'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Barcelona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8ecfb716-0962-4564-bd40-894b7727e1ca'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8d353cf3-71ee-4010-84b3-4aa26af85107'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'37b988f6-c28b-4a26-980c-cde122e0783d',
'Shaddai Heidgen',
'Ramon Trias Fargas 25-27 08005 Barcelona',
'Post-Doctoral Research Associate',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37b988f6-c28b-4a26-980c-cde122e0783d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37b988f6-c28b-4a26-980c-cde122e0783d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37b988f6-c28b-4a26-980c-cde122e0783d'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Barcelona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '37b988f6-c28b-4a26-980c-cde122e0783d'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8d353cf3-71ee-4010-84b3-4aa26af85107'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'5420fbc9-c4e4-4a70-9bcf-ca83e2375574',
'Marco Madella',
'Ramon Trias Fargas 25-27 08005 Barcelona',
'Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '5420fbc9-c4e4-4a70-9bcf-ca83e2375574'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '5420fbc9-c4e4-4a70-9bcf-ca83e2375574'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '5420fbc9-c4e4-4a70-9bcf-ca83e2375574'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Barcelona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '5420fbc9-c4e4-4a70-9bcf-ca83e2375574'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8d353cf3-71ee-4010-84b3-4aa26af85107'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'de2465c6-e97f-4794-8ec3-1f59b826f9a7',
'Hèctor Aleix Orengo Romeu',
'Plaça d\'en Rovellat, s/n, 43003 Tarragona',
'Co-Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'de2465c6-e97f-4794-8ec3-1f59b826f9a7'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Spain' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'de2465c6-e97f-4794-8ec3-1f59b826f9a7'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Catalunya' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Region'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'de2465c6-e97f-4794-8ec3-1f59b826f9a7'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Tarragona' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'de2465c6-e97f-4794-8ec3-1f59b826f9a7'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'd1895d4f-20d2-4521-8a48-65e6f02bcb9f'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'b963781b-613f-409c-8172-1107ed48e1c5',
'Sebastian Fajardo Bernal',
'Snellius Niels Bohrweg 1 2333 CA Leiden',
'Co-Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'b963781b-613f-409c-8172-1107ed48e1c5'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Netherlands' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'b963781b-613f-409c-8172-1107ed48e1c5'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'South Holland' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Province'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'b963781b-613f-409c-8172-1107ed48e1c5'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Leiden' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE 'b963781b-613f-409c-8172-1107ed48e1c5'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '35b321fa-8ee8-4176-abf2-bc184fb0806a'));

INSERT INTO public.person_organization_resource(id, id_maphsa, "name", place_address, description, person_organization_category, actor_role_type, actor_role_type_from, actor_role_type_to) VALUES
(DEFAULT,
'8e6471c3-7be9-4816-89dc-d7e8d9e5fba0',
'Juan Carlos Vargas Ruiz',
'Carrera 32 No 22 - 08 Santa Marta D.T.C.H. - Colombia Código Postal No. 470004',
'Co-Principal Investigator',
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Person or Organization Category') AND ct.concept_string LIKE 'Person'),
(SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus ct WHERE ct."name" LIKE 'Actor Role Type') AND ct.concept_string LIKE 'Archaeological Research'),
'2024-01-01 00:00:00.001',
'2025-12-31 23:59:59.001')
;

INSERT INTO public.pers_org_res_adm_div
(pers_org_res_id, her_admin_div_id)
VALUES
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8e6471c3-7be9-4816-89dc-d7e8d9e5fba0'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Netherlands' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Country'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8e6471c3-7be9-4816-89dc-d7e8d9e5fba0'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'South Holland' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Province'))),
((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8e6471c3-7be9-4816-89dc-d7e8d9e5fba0'),(SELECT had.id FROM her_admin_div had WHERE had.admin_div_name LIKE 'Leiden' AND had.admin_type = (SELECT ct.concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = (SELECT id FROM concept_thesaurus cth WHERE cth."name" LIKE 'Administrative Division Type') AND ct.concept_string LIKE 'Municipality')));

INSERT INTO public.related_person_organization
(person_organization_1, person_organization_2)
VALUES((SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '8e6471c3-7be9-4816-89dc-d7e8d9e5fba0'),(SELECT por.id FROM person_organization_resource por WHERE por.id_maphsa LIKE '2f33013f-9d7e-48a0-9768-a977020fcc23'));

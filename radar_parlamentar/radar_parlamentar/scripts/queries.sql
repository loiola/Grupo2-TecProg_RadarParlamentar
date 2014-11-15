-- Some useful SQL queries

-- List of lawmakers for a legislative house:
SELECT par.nome, par.genero, leg.inicio, leg.fim, leg.localidade, part.nome
FROM (modelagem_legislatura AS leg JOIN modelagem_partido AS part ON leg.partido_id = part.id)
JOIN modelagem_parlamentar AS par ON par.id = leg.parlamentar_id
WHERE leg.casa_legislativa_id = ID_CASA_LEGISLATIVA;

-- Count how many MPs are there in a legislative house
SELECT count(*)
FROM modelagem_legislatura AS leg
JOIN modelagem_parlamentar AS par ON par.id = leg.parlamentar_id
WHERE leg.casa_legislativa_id = ID_CASA_LEGISLATIVA;

-- Concatenated list polls to his proposals for legislative house
SELECT vot.id_vot, vot.descricao, vot.data, prop.sigla, prop.numero, prop.ano
FROM modelagem_votacao AS vot
JOIN modelagem_proposicao AS prop ON vot.proposicao_id = prop.id
WHERE prop.casa_legislativa_id = ID_CASA_LEGISLATIVA;

-- Counts how many polls have a home legsilativa
SELECT count(*)
FROM modelagem_votacao AS vot
JOIN modelagem_proposicao AS prop ON vot.proposicao_id = prop.id
WHERE prop.casa_legislativa_id = ID_CASA_LEGISLATIVA;

-- Counts how many polls have in each legislative house
SELECT prop.casa_legislativa_id, count(*)
FROM modelagem_votacao AS vot
JOIN modelagem_proposicao AS prop ON vot.proposicao_id = prop.id
GROUP BY prop.casa_legislativa_id;



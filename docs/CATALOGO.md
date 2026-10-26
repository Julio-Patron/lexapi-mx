# Catálogo de Lex API MX

Corte: **2026-10-26**. Las cifras corresponden a esa fecha; el estado vigente hoy se consulta en `GET /api/v1/corpus/status`.

## Cobertura

| Concepto | Total |
|---|---|
| Ordenamientos federales | 198 |
| Artículos vigentes | 36,332 |
| Disposiciones vigentes (artículos, fracciones, incisos, capítulos y demás) | 115,367 |
| Disposiciones con fuente oficial y checksum SHA-256 | 100% |

Jurisdicción: **federal**. Las normas estatales y municipales no están incluidas.

Fuentes oficiales del texto: Cámara de Diputados (`diputados.gob.mx`, 114,068 disposiciones), Diario Oficial de la Federación (`dof.gob.mx`, 321), STPS (`siaat.stps.gob.mx`, 840) y el Tribunal de Justicia Administrativa de la CDMX (`tjacdmx.gob.mx`, 138).

Última reforma incorporada: Constitución, DOF 2026-10-07 (nacionalidad única para titulares de los Ejecutivos federal y locales; artículos 82, 116 y 122), vigente desde el 2026-10-08.

Cobertura temporal: texto vigente con trazabilidad prospectiva desde la incorporación de cada norma. Una consulta anterior al inicio de cobertura devuelve `outside_coverage`; no se reconstruye historia general.

El catálogo vivo se consulta con `GET /api/v1/normas` (scope `norms:read`).

## Constitución (1)

| Clave | Slug | Nombre oficial |
|---|---|---|
| `CPEUM` | `cpeum` | Constitución Política de los Estados Unidos Mexicanos |

## Códigos (9)

| Clave | Slug | Nombre oficial |
|---|---|---|
| `CCF` | `ccf` | Código Civil Federal |
| `CCOM` | `ccom` | Código de Comercio |
| `CJM` | `cjm` | Código de Justicia Militar |
| `CFPC` | `cfpc` | Código Federal de Procedimientos Civiles |
| `CFF` | `cff` | Código Fiscal de la Federación |
| `CMPP` | `cmpp` | Código Militar de Procedimientos Penales |
| `CNPCF` | `cnpcf` | Código Nacional de Procedimientos Civiles y Familiares |
| `CNPP` | `cnpp` | Código Nacional de Procedimientos Penales |
| `CPF` | `cpf` | Código Penal Federal |

## Leyes (119)

| Clave | Slug | Nombre oficial |
|---|---|---|
| `LA` | `ladua` | Ley Aduanera |
| `LAgra` | `lagra` | LEY Agraria |
| `LAASSP` | `laassp` | Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público |
| `LACP` | `lacp` | Ley de Ahorro y Crédito Popular |
| `Ley de Amparo` | `ley_amparo` | Ley de Amparo, Reglamentaria de los artículos 103 y 107 de la Constitución Política de los Estados Unidos Mexicanos |
| `LASoc` | `lasoc` | Ley de Asistencia Social |
| `LAPP` | `lapp` | Ley de Asociaciones Público Privadas |
| `LAAT` | `laat` | Ley de Ayuda Alimentaria para los Trabajadores |
| `LBOGM` | `lbogm` | LEY de Bioseguridad de Organismos Genéticamente Modificados |
| `LCEC` | `lcec` | Ley de Cámaras Empresariales y sus Confederaciones |
| `LCE` | `lce` | Ley de Comercio Exterior |
| `LCM` | `lcm` | Ley de Concursos Mercantiles |
| `LCF` | `lcf` | Ley de Coordinación Fiscal |
| `LDFEFM` | `ldfefm` | Ley de Disciplina Financiera de las Entidades Federativas y los Municipios |
| `LFEA` | `lfea` | Ley de Firma Electrónica Avanzada |
| `LFRCF` | `lfrcf` | Ley de Fiscalización y Rendición de Cuentas de la Federación |
| `LFCC` | `lfcc` | Ley de Fomento a la Confianza Ciudadana |
| `LFAAR` | `lfaar` | Ley de Fondos de Aseguramiento Agropecuario y Rural |
| `LFI` | `lfi` | Ley de Fondos de Inversión |
| `LICAL` | `lical` | Ley de Infraestructura de la Calidad |
| `LIC` | `lic` | Ley de Instituciones de Crédito |
| `LISF` | `lisf` | Ley de Instituciones de Seguros y de Fianzas |
| `LIE` | `lie` | Ley de Inversión Extranjera |
| `LCNBV` | `lcnbv` | Ley de la Comisión Nacional Bancaria y de Valores |
| `LESS` | `less` | Ley de la Economía Social y Solidaria |
| `LSAR` | `lsar` | Ley de los Sistemas de Ahorro para el Retiro |
| `LMigra` | `lmigra` | Ley de Migración |
| `LNCM` | `lncm` | Ley de Navegación y Comercio Marítimos |
| `LOPSRM` | `lopsrm` | Ley de Obras Públicas y Servicios Relacionados con las Mismas |
| `LPLAN` | `lplan` | Ley de Planeación |
| `LPO` | `lpo` | LEY de Productos Orgánicos |
| `LPAB` | `lpab` | Ley de Protección al Ahorro Bancario |
| `LPDUSF` | `lpdusf` | Ley de Protección y Defensa al Usuario de Servicios Financieros |
| `LSP` | `lsp` | Ley de Sistemas de Pagos |
| `LSRLIP` | `lsrlip` | Ley de Sociedades de Responsabilidad Limitada de Interés Público |
| `LSSS` | `lsss` | Ley de Sociedades de Solidaridad Social |
| `LTF` | `ltf` | Ley de Tesorería de la Federación |
| `LTFCCG` | `ltfccg` | Ley de Transparencia y de Fomento a la Competencia en el Crédito Garantizado |
| `LUC` | `luc` | Ley de Uniones de Crédito |
| `LViv` | `lviv` | Ley de Vivienda |
| `LBM` | `lbm` | Ley del Banco de México |
| `LIVA` | `liva` | Ley del Impuesto al Valor Agregado |
| `LIEPS` | `lieps` | Ley del Impuesto Especial sobre Producción y Servicios |
| `LISR` | `lisr` | Ley del Impuesto sobre la Renta |
| `LISSSTE` | `lissste` | Ley del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |
| `Ley del Infonavit` | `ley_infonavit` | Ley del Instituto del Fondo Nacional de la Vivienda para los Trabajadores |
| `LIFNCT` | `lifnct` | Ley del Instituto del Fondo Nacional para el Consumo de los Trabajadores |
| `LMV` | `lmv` | Ley del Mercado de Valores |
| `LSS` | `lss` | Ley del Seguro Social |
| `LSAT` | `lsat` | Ley del Servicio de Administración Tributaria |
| `LFAR` | `lfar` | Ley Federal de Austeridad Republicana |
| `LFCE` | `lfce` | Ley Federal de Competencia Económica |
| `LFCP` | `lfcp` | Ley Federal de Correduría Pública |
| `LFD` | `lfd` | Ley Federal de Derechos |
| `LFDP` | `lfdp` | Ley Federal de Deuda Pública |
| `LFEP` | `lfep` | Ley Federal de las Entidades Paraestatales |
| `LFDC` | `lfdc` | Ley Federal de los Derechos del Contribuyente |
| `LFTSE` | `lftse` | Ley Federal de los Trabajadores al Servicio del Estado, Reglamentaria del Apartado B) del Artículo 123 Constitucional |
| `LFPRH` | `lfprh` | Ley Federal de Presupuesto y Responsabilidad Hacendaria |
| `LFPA` | `lfpa` | Ley Federal de Procedimiento Administrativo |
| `LFPCA` | `lfpca` | Ley Federal de Procedimiento Contencioso Administrativo |
| `LFPCCS` | `lfpccs` | LEY Federal de Producción, Certificación y Comercio de Semillas |
| `LFPPI` | `lfppi` | Ley Federal de Protección a la Propiedad Industrial |
| `LFPC` | `lfpc` | Ley Federal de Protección al Consumidor |
| `LFPDPPP` | `lfpdppp` | Ley Federal de Protección de Datos Personales en Posesión de los Particulares |
| `LFREMSP` | `lfremsp` | Ley Federal de Remuneraciones de los Servidores Públicos |
| `LFRA` | `lfra` | Ley Federal de Responsabilidad Ambiental |
| `LFRPE` | `lfrpe` | Ley Federal de Responsabilidad Patrimonial del Estado |
| `LFRSP` | `lfrsp` | Ley Federal de Responsabilidades de los Servidores Públicos |
| `LFSA` | `lfsa` | LEY Federal de Sanidad Animal |
| `LFSV` | `lfsv` | LEY Federal de Sanidad Vegetal |
| `LFVV` | `lfvv` | LEY Federal de Variedades Vegetales |
| `LFDA` | `lfda` | Ley Federal del Derecho de Autor |
| `LISAN` | `lisan` | Ley Federal del Impuesto sobre Automóviles Nuevos |
| `LFT` | `lft` | Ley Federal del Trabajo |
| `LFPIORPI` | `lfpiorpi` | Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita |
| `LGA` | `lga` | Ley General de Archivos |
| `LGBN` | `lgbn` | Ley General de Bienes Nacionales |
| `LGCC` | `lgcc` | Ley General de Cambio Climático |
| `LGCG` | `lgcg` | Ley General de Contabilidad Gubernamental |
| `LGDFS` | `lgdfs` | LEY General de Desarrollo Forestal Sustentable |
| `LGMASC` | `lgmasc` | Ley General de Mecanismos Alternativos de Solución de Controversias |
| `LGOAAC` | `lgoaac` | Ley General de Organizaciones y Actividades Auxiliares del Crédito |
| `LGP` | `lgp` | Ley General de Población |
| `LGPDPPSO` | `lgpdppso` | Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados |
| `LGRA` | `lgra` | Ley General de Responsabilidades Administrativas |
| `LGS` | `lgs` | Ley General de Salud |
| `LGSC` | `lgsc` | Ley General de Sociedades Cooperativas |
| `LGSM` | `lgsm` | Ley General de Sociedades Mercantiles |
| `LGTOC` | `lgtoc` | Ley General de Títulos y Operaciones de Crédito |
| `LGTAIP` | `lgt` | Ley General de Transparencia y Acceso a la Información Pública |
| `LGVS` | `lgvs` | LEY General de Vida Silvestre |
| `LGEEPA` | `lgeepa` | Ley General del Equilibrio Ecológico y la Protección al Ambiente |
| `LGSNA` | `lgsna` | Ley General del Sistema Nacional Anticorrupción |
| `LGPGIR` | `lgpgir` | Ley General para la Prevención y Gestión Integral de los Residuos |
| `LMEUM` | `lmeum` | Ley Monetaria de los Estados Unidos Mexicanos |
| `LNEP` | `lnep` | Ley Nacional de Ejecución Penal |
| `LNSIJPA` | `lnsijpa` | Ley Nacional del Sistema Integral de Justicia Penal para Adolescentes |
| `LNETB` | `lnetb` | Ley Nacional para Eliminar Trámites Burocráticos |
| `LOAPF` | `loapf` | Ley Orgánica de la Administración Pública Federal |
| `LOPDC` | `lopdc` | Ley Orgánica de la Procuraduría de la Defensa del Contribuyente |
| `LONAFIN` | `lonafin` | Ley Orgánica de Nacional Financiera |
| `LOSHF` | `loshf` | Ley Orgánica de Sociedad Hipotecaria Federal |
| `LOBB` | `lobb` | Ley Orgánica del Banco del Bienestar |
| `LOBNCE` | `lobnce` | Ley Orgánica del Banco Nacional de Comercio Exterior |
| `LOBNOSP` | `lobnosp` | Ley Orgánica del Banco Nacional de Obras y Servicios Públicos |
| `LOBANJERCITO` | `lobanjercito` | Ley Orgánica del Banco Nacional del Ejército, Fuerza Aérea y Armada |
| `LOCFCRL` | `locfcrl` | Ley Orgánica del Centro Federal de Conciliación y Registro Laboral |
| `LDVUMA` | `ldvuma` | Ley para Determinar el Valor de la Unidad de Medida y Actualización |
| `LDCMPME` | `ldcmpme` | Ley para el Desarrollo de la Competitividad de la Micro, Pequeña y Mediana Empresa |
| `LIISPCEN` | `liispcen` | Ley para Impulsar el Incremento Sostenido de la Productividad y la Competitividad de la Economía Nacional |
| `LTOSF` | `ltosf` | Ley para la Transparencia y Ordenamiento de los Servicios Financieros |
| `LTPCPIMCP` | `ltpcpimcp` | Ley para la Transparencia, Prevención y Combate de Prácticas Indebidas en Materia de Contratación de Publicidad |
| `LRASCAP` | `lrascap` | Ley para Regular las Actividades de las Sociedades Cooperativas de Ahorro y Préstamo |
| `LRAF` | `lraf` | Ley para Regular las Agrupaciones Financieras |
| `LRITF` | `lritf` | Ley para Regular las Instituciones de Tecnología Financiera |
| `LRSIC` | `lrsic` | Ley para Regular las Sociedades de Información Crediticia |
| `LFGFAGA` | `lfgfaga` | Ley que Crea el Fondo de Garantía y Fomento para la Agricultura, Ganadería y Avicultura |
| `LCS` | `lcs` | Ley Sobre el Contrato de Seguro |

## Reglamentos (69)

| Clave | Slug | Nombre oficial |
|---|---|---|
| `RLA` | `reg_ladua` | Reglamento de la Ley Aduanera |
| `RLA-MOPR` | `reg_lagra_mopr` | REGLAMENTO de la Ley Agraria en Materia de Ordenamiento de la Propiedad Rural |
| `RLA-FODMC` | `reg_lagra_fodmc` | REGLAMENTO de la Ley Agraria para Fomentar la Organización y Desarrollo de la Mujer Campesina |
| `RLAASSP` | `reg_laassp` | Reglamento de la Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público |
| `RLAPP` | `reg_lapp` | Reglamento de la Ley de Asociaciones Público Privadas |
| `RLAAT` | `reg_laat` | Reglamento de la Ley de Ayuda Alimentaria para los Trabajadores |
| `RLBOGM` | `reg_lbogm` | REGLAMENTO de la Ley de Bioseguridad de Organismos Genéticamente Modificados |
| `RLCEC` | `reg_lcec` | Reglamento de la Ley de Cámaras Empresariales y sus Confederaciones |
| `RLCE` | `reg_lce` | Reglamento de la Ley de Comercio Exterior |
| `RLFEA` | `reg_lfea` | Reglamento de la Ley de Firma Electrónica Avanzada |
| `RLICAL` | `reg_lical` | Reglamento de la Ley de Infraestructura de la Calidad |
| `RLIE-RNIE` | `reg_lie_rnie` | Reglamento de la Ley de Inversión Extranjera y del Registro Nacional de Inversiones Extranjeras |
| `RLSAR` | `reg_lsar` | Reglamento de la Ley de los Sistemas de Ahorro para el Retiro |
| `RLMigra` | `reg_lmigra` | Reglamento de la Ley de Migración |
| `RLOPSRM` | `reg_lopsrm` | Reglamento de la Ley de Obras Públicas y Servicios Relacionados con las Mismas |
| `RLPO` | `reg_lpo` | REGLAMENTO de la Ley de Productos Orgánicos |
| `RLTF` | `reg_ltf` | Reglamento de la Ley de Tesorería de la Federación |
| `RLIVA` | `reg_liva` | Reglamento de la Ley del Impuesto al Valor Agregado |
| `RLIEPS` | `reg_lieps` | Reglamento de la Ley del Impuesto Especial sobre Producción y Servicios |
| `RLISR` | `reg_lisr` | Reglamento de la Ley del Impuesto sobre la Renta |
| `RINFONAVIT-TAI` | `reg_infonavit_tai` | Reglamento de la Ley del Instituto del Fondo Nacional de la Vivienda para los Trabajadores en Materia de Transparencia y Acceso a la Información |
| `RLIFNCT` | `reg_lifnct` | Reglamento de la Ley del Instituto del Fondo Nacional para el Consumo de los Trabajadores |
| `RLSS-MAEBA` | `reg_lss_bienes_adjudicados` | Reglamento de la Ley del Seguro Social en Materia de Administración y Enajenación de Bienes Adjudicados |
| `RLSS-MACERF` | `reg_lss_macerf` | Reglamento de la Ley del Seguro Social en Materia de Afiliación, Clasificación de Empresas, Recaudación y Fiscalización |
| `RLSS-RFARGFA` | `reg_lss_reservas_financieras` | Reglamento de la Ley del Seguro Social para la Constitución, Inversión y Uso para la Operación de las Reservas Financieras y Actuariales y del Fondo para el Cumplimiento de Obligaciones Laborales de Carácter Legal o Contractual |
| `RLFCE` | `reg_lfce` | Reglamento de la Ley Federal de Competencia Económica |
| `RLFCP` | `reg_lfcp` | Reglamento de la Ley Federal de Correduría Pública |
| `RLFEP` | `reg_lfep` | Reglamento de la Ley Federal de las Entidades Paraestatales |
| `RLFPRH` | `reg_lfprh` | Reglamento de la Ley Federal de Presupuesto y Responsabilidad Hacendaria |
| `RLFPCCS` | `reg_lfpccs` | REGLAMENTO de la Ley Federal de Producción, Certificación y Comercio de Semillas |
| `RLFPPI` | `reg_lfppi` | Reglamento de la Ley Federal de Protección a la Propiedad Industrial |
| `RLFPC` | `reg_lfpc` | Reglamento de la Ley Federal de Protección al Consumidor |
| `RLFSA` | `reg_lfsa` | REGLAMENTO de la Ley Federal de Sanidad Animal |
| `RLFSV` | `reg_lfsv` | REGLAMENTO de la Ley Federal de Sanidad Vegetal |
| `RLFVV` | `reg_lfvv` | REGLAMENTO de la Ley Federal de Variedades Vegetales |
| `RLFDA` | `reg_lfda` | Reglamento de la Ley Federal del Derecho de Autor |
| `RLFPIORPI` | `reg_lfpiorpi` | Reglamento de la Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita |
| `RLGCC-RNE` | `reg_lgcc_emisiones` | Reglamento de la Ley General de Cambio Climático en Materia del Registro Nacional de Emisiones |
| `RLGDFS` | `reg_lgdfs` | REGLAMENTO de la Ley General de Desarrollo Forestal Sustentable |
| `RLGP` | `reg_lgp` | Reglamento de la Ley General de Población |
| `RLGS-CSAEPS` | `reg_lgs_control_sanitario_establecimientos` | Reglamento de la Ley General de Salud en Materia de Control Sanitario de Actividades, Establecimientos, Productos y Servicios |
| `RLGS-CSOTC` | `reg_lgs_organos_tejidos_cadaveres` | Reglamento de la Ley General de Salud en Materia de Control Sanitario de la Disposición de Órganos, Tejidos y Cadáveres de Seres Humanos |
| `RLGS-CANNABIS` | `reg_lgs_cannabis_medicinal` | Reglamento de la Ley General de Salud en Materia de Control Sanitario para la Producción, Investigación y Uso Medicinal de la Cannabis y sus Derivados Farmacológicos |
| `RLGS-MIS` | `reg_lgs_investigacion` | Reglamento de la Ley General de Salud en Materia de Investigación para la Salud |
| `RLGS-MPSAM` | `reg_lgs_atencion_medica` | Reglamento de la Ley General de Salud en Materia de Prestación de Servicios de Atención Médica |
| `RLGS-MP` | `reg_lgs_publicidad` | Reglamento de la Ley General de Salud en Materia de Publicidad |
| `RLGS-MSI` | `reg_lgs_sanidad_internacional` | Reglamento de la Ley General de Salud en Materia de Sanidad Internacional |
| `RLGS-MT` | `reg_lgs_trasplantes` | Reglamento de la Ley General de Salud en Materia de Trasplantes |
| `RLGVS` | `reg_lgvs` | REGLAMENTO de la Ley General de Vida Silvestre |
| `RLGEEPA-ANP` | `reg_lgeepa_anp` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Áreas Naturales Protegidas |
| `RLGEEPA-AAA` | `reg_lgeepa_auditorias` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Autorregulación y Auditorías Ambientales |
| `RLGEEPA-EIA` | `reg_lgeepa_impacto` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Evaluación del Impacto Ambiental |
| `RLGEEPA-OE` | `reg_lgeepa_ordenamiento` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Ordenamiento Ecológico |
| `RLGEEPA-PCCA` | `reg_lgeepa_atmosfera` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Prevención y Control de la Contaminación de la Atmósfera |
| `RLGEEPA-RETC` | `reg_lgeepa_emisiones` | Reglamento de la Ley General del Equilibrio Ecológico y la Protección al Ambiente en Materia de Registro de Emisiones y Transferencia de Contaminantes |
| `RLGPGIR` | `reg_lgpgir` | Reglamento de la Ley General para la Prevención y Gestión Integral de los Residuos |
| `RLDCMPME` | `reg_ldcmpme` | Reglamento de la Ley para el Desarrollo de la Competitividad de la Micro, Pequeña y Mediana Empresa |
| `RLFT-121-122` | `reg_lft_art121_122` | Reglamento de los Artículos 121 y 122 de la Ley Federal del Trabajo |
| `RSHMATSPF` | `reg_lftse_seguridad_higiene` | Reglamento de Seguridad, Higiene y Medio Ambiente en el Trabajo del Sector Público Federal |
| `RISSSTE-MEDICOS` | `reg_lissste_servicios_medicos` | Reglamento de Servicios Médicos del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |
| `RLFPC-122` | `reg_lfpc_art122` | Reglamento del Artículo 122 de la Ley Federal de Protección al Consumidor |
| `RCCOM-PSC` | `reg_ccom_psc` | Reglamento del Código de Comercio en Materia de Prestadores de Servicios de Certificación |
| `RCFF` | `reg_cff` | Reglamento del Código Fiscal de la Federación |
| `RISSSTE-AFILIACION` | `reg_lissste_afiliacion_vigencia` | Reglamento del Sistema Nacional de Afiliación y Vigencia de Derechos, de la Base de Datos Única de Derechohabientes y del Expediente Electrónico Único del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |
| `RFSST` | `reg_lft_seguridad_salud` | Reglamento Federal de Seguridad y Salud en el Trabajo |
| `RIINDAABIN` | `reg_int_indaabin` | Reglamento Interior del Instituto de Administración y Avalúos de Bienes Nacionales |
| `RISSSTE-PENSIONES-10T` | `reg_lissste_pensiones_decimo_transitorio` | Reglamento para el Otorgamiento de Pensiones de los Trabajadores Sujetos al Régimen del Artículo Décimo Transitorio del Decreto por el que se expide la Ley del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |
| `RISSSTE-PENSIONES-CI` | `reg_lissste_pensiones_cuentas_individuales` | Reglamento para el Otorgamiento de Pensiones del Régimen de Cuentas Individuales del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |
| `RISSSTE-RIESGOS` | `reg_lissste_riesgos_invalidez` | Reglamento para la Dictaminación en Materia de Riesgos del Trabajo e Invalidez del Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado |

## Operaciones y créditos

| Operación | Endpoint | Evento | Créditos |
|---|---|---|---|
| Listar normas | `GET /api/v1/normas` | `norm.list` | 1 |
| Obtener norma | `GET /api/v1/normas/{slug}` | `norm.get` | 1 |
| Estructura de una norma | `GET /api/v1/normas/{slug}/estructura` | `norm.structure` | 1 (el texto completo, `include_text`, solo en planes de la API) |
| Buscar artículos | `GET /api/v1/articulos/search` | `article.search` | 1 (hasta 50 resultados en planes de la API; hasta 10 en el gratuito) |
| Obtener artículo | `GET /api/v1/articulos/{id}` | `article.get` | 1 |
| Historial de un artículo | `GET /api/v1/articulos/{id}/historial` | `article.history` | 1 |
| Resolver una cita o consulta | `POST /api/v1/resolve` | `resolution.run` | 1 |
| Mapa normativo | `POST /api/v1/map` | `normative_map.run` | 2 (sin tema detectado, `coverage_status: not_found`, no se cobra) |

Solo se cobran respuestas exitosas (2xx) con resultado: una búsqueda sin artículos, un `resolve` sin items y una consulta con una fecha anterior al inicio de cobertura (`outside_coverage`) no se cobran. Un reintento con el mismo `Idempotency-Key` y la misma petición no se cobra dos veces; la clave queda atada al contenido (método, ruta, query y cuerpo).

## Planes

| Plan | Incluye | Precio (MXN, IVA incluido) |
|---|---|---|
| Gratis | 500 créditos por mes calendario (hora de la Ciudad de México), sin acumulación; API y servidor MCP; hasta 2 claves; 10 peticiones por minuto y 200 por día por cuenta; búsquedas de hasta 10 artículos; sin mapa normativo ni texto completo de normas | $0 |
| API Inicial | 10,000 créditos al mes; mapa normativo y texto completo de normas; hasta 10 claves; 120 peticiones por minuto por clave | $499 al mes o $4,990 al año |
| API Profesional | 50,000 créditos al mes; mapa normativo y texto completo de normas; hasta 10 claves; 120 peticiones por minuto por clave | $1,499 al mes o $14,990 al año |
| Recarga | 1,000 créditos que no caducan | $100 |
| Institucional | Volumen, condiciones y SLA negociados | A la medida |

Cuando un cliente prepago se queda sin saldo, la API responde `402` con el código `insufficient_credits` y el enlace de recarga.

## Servidor MCP

| Herramienta | Endpoint |
|---|---|
| `resolve_legal_citation` | `POST /api/v1/resolve` |
| `search_mexican_law` | `GET /api/v1/articulos/search` |
| `get_norm_structure` | `GET /api/v1/normas/{slug}/estructura` |

Instalación: [`MCP_QUICKSTART.md`](MCP_QUICKSTART.md).

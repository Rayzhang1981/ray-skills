# CAMEO 物性数据导航（增强版）

本文件是「1-物性数据/CAMEO」文件夹（1306 个 CAMEO 化学品数据表）的索引，含中文名与 CAS。

## 检索规则（Agent 专用）
1. 用户给出中文名/英文名/CAS/缩写，先定位到下表对应行；
2. 取该行的 media_id；
3. 调 `mcp__ima-mcp__fetch_media_content`（media_id）精确读取该文件；
4. 从内容解析 NFPA 704(8.5)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4) 等。

> ⚠️ **运行层差异（2026-09-14 加）**：`fetch_media_content` 仅 WorkBuddy 侧的 ima 连接器提供；
> DSH 侧（本地 stdio 桥接器）没有此工具，走到第 3 步会报 unknown tool。
> DSH 下的替代：先用本 skill 的本地离线索引（1-物性数据等 13 类）取数；缺项时请用户在 WorkBuddy 侧读取，**不要反复重试**。

| 缩写 | 英文名 | 中文名 | CAS | 同义词 | media_id |
|------|--------|--------|-----|--------|----------|
| AAC | ACETIC ACID | 乙酸 | 64-19-7 |  | pdf_6a8faacca882a39304796eef402a5436_0af3eea23cf94a3848602e20ed31a7977410596022594182 |
| AAD | ACETALDEHYDE | 乙醛 | 75-07-0 | Acetic aldehydeEthanalEthyl aldehyde | pdf_6a8faacca882a39304796eef402a5436_5b1c339eec36c949375b27189ef5f3417410596022594182 |
| AAM | ACRYLAMIDE SOLUTION | 丙烯酰胺溶液 | 79-06-1 | Acrylic acid amide (50%)Acrylic amide 50%Propenamide (50%) | pdf_6a8faacca882a39304796eef402a5436_d02ea779c2b6ce1d77ae86aa59184d3b7410596022594182 |
| AAN | N-AMYL ALCOHOL | 正戊醇 | 71-41-0 | 1-Amyl alcoholn-Butycarbinol1-PentanolPentyl alcohol | pdf_6a8faacca882a39304796eef402a5436_e087a0a51e8243e18f06036b3af2e66e7410596022594182 |
| AAS | SEC-AMYL ACETATE | 乙酸仲戊酯 | 626-38-0 | Banana oilPear oil2-Pentylacelate | pdf_6a8faacca882a39304796eef402a5436_efccc3a533d1655fe16f39b1d59645517410596022594182 |
| AAT | AMMONIUM ACETATE | 乙酸铵 | 631-61-8 | Acetic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_32a2322961bbac85ef265cc172f4abf87410596022594182 |
| ABC | AMMONIUM BICARBONATE | 碳酸氢铵 | 1066-33-7 | Acid ammonium carbonateAmmonium hydrogen carbonateCarbonic acid, monoammoniumsal | pdf_6a8faacca882a39304796eef402a5436_b730551754da19c165ede35a2c7e22ba7410596022594182 |
| ABF | AMMONIUM BIFLUORIDE | 氟化氢铵 | 1341-49-7 | Acid ammonium fluorideAmmonium acid fluorideAmmonium hydrogen fluorideAmmonium h | pdf_6a8faacca882a39304796eef402a5436_c32334f5bd0b011a2720ea99030d9aa27410596022594182 |
| ABM | ACETYL BROMIDE | 乙酰溴 | 506-96-7 |  | pdf_6a8faacca882a39304796eef402a5436_2f32948eca09d067a3d5176c9f4956527410596022594182 |
| ABN | ALKYL(C | 烷基苯磺酸 |  | Decyibenzenesulfonic acidUn: do: tri: tetra penta or Hexabenzenesulfonic acidUn: | pdf_6a8faacca882a39304796eef402a5436_d8fc93945563da889733beca063d34f37410596022594182 |
| ABR | ALLYL BROMIDE | 烯丙基溴 | 106-95-6 |  | pdf_6a8faacca882a39304796eef402a5436_ff4cd55c8258aa3a99a9c3f8f3e9b6f07410596022594182 |
| ABZ | AMMONIUM BENZOATE | 苯甲酸铵 | 1863-63-4 | Benzoic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_d1ab66d7607a3f87e0491a17cb76af387410596022594182 |
| ACA | ACETIC ANHYDRIDE | 乙酸酐 | 108-24-7 | Acetyl oxideAcetic acid anhydrideEthanoc anhydride | pdf_6a8faacca882a39304796eef402a5436_777fc8d80dc1c229ffa7cec38c233aeb7410596022594182 |
| ACB | AMMONIUM CARBONATE | 碳酸铵 | 506-87-6 | Hartshorn Sal volatile | pdf_6a8faacca882a39304796eef402a5436_cb936f9b905e7054827b62eb3dda2ead7410596022594182 |
| ACC | ACETYL CHLORIDE | 乙酰氯 | 75-36-5 |  | pdf_6a8faacca882a39304796eef402a5436_ee1a798795b97e1cf36bd421932a32e87410596022594182 |
| ACD | ACRIDINE | 吖啶 | 260-94-6 | 10-AzaanthraceneBenzo (b) quinolineDibenzo [b,e] pyridine | pdf_6a8faacca882a39304796eef402a5436_32e42cbd97662a2a99a41597d552e3487410596022594182 |
| ACE | ACETYLENE | 乙炔 | 74-86-2 | EthineEthine | pdf_6a8faacca882a39304796eef402a5436_ff2089144e7c3e8c750c52a099b6dade7410596022594182 |
| ACF | ALLYL CHLOROFORMATE | 氯甲酸烯丙酯 | 2937-50-0 | Allyl chlorocarbonate | pdf_6a8faacca882a39304796eef402a5436_7c5d903dae32346be9dcea75be7b75037410596022594182 |
| ACH | AMMONIUM CHROMATE | 铬酸铵 | 7788-98-9 | Diamronium chromateNeutral ammonium chromate | pdf_6a8faacca882a39304796eef402a5436_b0b613ad060fafa7b8ce0b16e150baa97410596022594182 |
| ACI | AMMONIUM CITRATE, DIBASIC | 柠檬酸氢二铵 | 3012-65-5 | Ammonium citrateCitric acid, diammonium saltCitronmonium citrate | pdf_6a8faacca882a39304796eef402a5436_d3cf241dfdd9cb3e8c4e854d304577397410596022594182 |
| ACL | ALUMINUM CHLORIDE | 氯化铝 | 7446-70-0 | Anhydrous aluminum chloride | pdf_6a8faacca882a39304796eef402a5436_9b40e65ce64da8fbf565cdafb474447b7410596022594182 |
| ACM | AMMONIUM CARBAMATE | 氨基甲酸铵 | 1111-78-0 | Ammonium aminoformateAnhydride of ammoniumcarbonateCarbamic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_f34545bd20cee479e64ba6e47fe4fd157410596022594182 |
| ACN | ACRYLONITRILE | 丙烯腈 | 107-13-1 | CyanethyleneFumigrainVentoxVinyl cyanide | pdf_6a8faacca882a39304796eef402a5436_4fdf1cb2a1b922e4766a28024d1845d87410596022594182 |
| ACO | ALUMINUM CHLORIDE SOLUTION | 氯化铝溶液 | 7446-70-0 |  | pdf_6a8faacca882a39304796eef402a5436_a839fe457a56c4ca130e0ed6de979a417410596022594182 |
| ACP | ACETOPHENONE | 苯乙酮 | 98-86-2 |  | pdf_6a8faacca882a39304796eef402a5436_ae047009cb304c439ca4614a246800cf7410596022594182 |
| ACR | ACRYLIC ACID | 丙烯酸 | 79-10-7 |  | pdf_6a8faacca882a39304796eef402a5436_e4e759938e4b80c7de5f2689c1fb7eb67410596022594182 |
| ACT | ACETONE | 丙酮 | 67-64-1 | Dimethyl ketonePropanone2-Propanone | pdf_6a8faacca882a39304796eef402a5436_3fa093e94cbb2b477f18b4bed9c04f817410596022594182 |
| ACY | ACETONE CYANOHYDRIN | 丙酮氰醇 | 75-86-5 | alpha-Hydroxy isobutronitrie2+Hydroxy-2-methylpropanenitrile2-MethylactonitrileP | pdf_6a8faacca882a39304796eef402a5436_f2192fec8aeaef23a851abebaca14b9a7410596022594182 |
| ADA | ADIPIC ACID | 己二酸 | 124-04-9 | Adipinic acid1.4-Butanedcarboxylic acidHexanedioic acid | pdf_6a8faacca882a39304796eef402a5436_9c6d027b8d285211aaa3c86ebab916097410596022594182 |
| ADN | ADIPONITRILE | 己二腈 | 111-69-3 | 1.4-DicyanobutaneHexanedintritile | pdf_6a8faacca882a39304796eef402a5436_b421b253681b344d3e06c2f008a2cf8c7410596022594182 |
| AEC | AMYL ACETATE (ALL ISOMERS) | 乙酸戊酯（各异构体） | 628-63-7 | Amyl acetate, mixed isomersAcetic acid, n-amyl esterPentyl acetates | pdf_6a8faacca882a39304796eef402a5436_f97f823c8f597d21b12a202bfcb335567410596022594182 |
| AEE | AMINOETHYLETHANOLAMINE | 氨乙基乙醇胺 | 111-41-1 | 2-[-(2-Aminoethyl) amino]2-(-(2-Aminoethyl) ethanolN-(2-Aminoethyl) ethanolamine | pdf_6a8faacca882a39304796eef402a5436_cf9ad1d246fee6ff223db11f3e06c9437410596022594182 |
| AEL | ACETAL | 缩醛 | 105-57-7 | Acetaldehyde diethylacetal1.1-DiethoxytaneDiethyl acetalEthylidene diethyletherU | pdf_6a8faacca882a39304796eef402a5436_eb764e5bb444fc3524e39de1a69054bc7410596022594182 |
| AEP | N-AMINOETHYL PIPERAZINE | N-氨乙基哌嗪 | 140-31-8 | 1-(2-Aminoethyl) piperazineN-(2-Aminoethyl) piperazine1-Piperazine ethanolamineU | pdf_6a8faacca882a39304796eef402a5436_7a4630c09c710f43f1fcc2fb7730fa247410596022594182 |
| AFB | AMMONIUM FLUOBORATE | 氟硼酸铵 | 13826-83-0 | Ammonium borofluorideAmmonium tetrafluoborate | pdf_6a8faacca882a39304796eef402a5436_09aa54829f20a799ab58f3759d39bc767410596022594182 |
| AFM | AMMONIUM FORMATE | 甲酸铵 | 540-69-2 | Fomic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_786ac8207102c829c8d65589f6edd1177410596022594182 |
| AFR | AMMONIUM FLUORIDE | 氟化铵 | 12125-01-8 | Neutral ammonium fluoride | pdf_6a8faacca882a39304796eef402a5436_d63f90a0a6cf9f4dc5479e778e6a04bb7410596022594182 |
| AGC | AMMONIUM GLUCONATE | 葡萄糖酸铵 | 19222-41-4 |  | pdf_6a8faacca882a39304796eef402a5436_a91270873feeee12f9363a046d26f4e57410596022594182 |
| AHP | AMMONIUM HYPOPHOSPHITE | 次磷酸铵 |  | Phosphinic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_40dec99b1dab25a41608a1d5c22cc2e97410596022594182 |
| AID | AMMONIUM IODIDE | 碘化铵 | 12027-06-4 |  | pdf_6a8faacca882a39304796eef402a5436_f3c793b55af0470adcf3c4fcdf6fb3a87410596022594182 |
| ALA | ALLYL ALCOHOL | 烯丙醇 | 107-18-6 | 2-Propen-1-olVinyl carbinol | pdf_6a8faacca882a39304796eef402a5436_de455b3c072c0761d647bad103a0d4977410596022594182 |
| ALC | ALLYL CHLORIDE | 烯丙基氯 | 107-05-1 | 3-Chloropropene3-Chloroproplene | pdf_6a8faacca882a39304796eef402a5436_ac60059b239468a1bce6d53bac4005ee7410596022594182 |
| ALD | ALDRIN | 艾氏剂 | 309-00-2 | 1.2.3,4,10.10-Hexachloro-1.4,4a,5,8,8a-hexahydro-1,4-endo-exo-5,8-dimethanaphtha | pdf_6a8faacca882a39304796eef402a5436_7a8762f3667f6f2dd2b28da029d6c3b67410596022594182 |
| ALF | ALUMINUM FLUORIDE | 氟化铝 | 7784-18-1 |  | pdf_6a8faacca882a39304796eef402a5436_ca0d5deae16b8cbd8d0183095e8673d27410596022594182 |
| ALM | ALUMINUM SULFATE | 硫酸铝 | 10043-01-3 | AlumCake aluminiumPaper maker&#x27 s alumPatent aluminum | pdf_6a8faacca882a39304796eef402a5436_1c1f139647f7a742f6696696ea5be8cb7410596022594182 |
| ALN | ALUMINUM NITRATE | 硝酸铝 | 13473-90-0 | Aluminum nitrate nonahydateNitric acid, aluminum salt | pdf_6a8faacca882a39304796eef402a5436_c0bf615847c3c7abc7948bfe1cc69fdf7410596022594182 |
| ALS | AMMONIUM LAURYL SULFATE | 十二烷基硫酸铵 | 2235-54-3 | Dodecyl sulfate, ammonium saltLauryl ammonium sulfate | pdf_6a8faacca882a39304796eef402a5436_b4cdec5c1840a19a9ee00ddb1acb97b97410596022594182 |
| ALT | AMMONIUM LACTATE | 乳酸铵 | 515-98-0 | Ammonium lactate syrupDL-Lactic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_bc21729bbcced25938b850ccc2ea6e467410596022594182 |
| AMA | AMMONIA, ANHYDROUS | 氨（无水） | 7664-41-7 | Liquid ammonia | pdf_6a8faacca882a39304796eef402a5436_da1267972b954bf31cca1d8d351a4e7a7410596022594182 |
| AMB | AMMONIUM MOLYBDATE | 钼酸铵 | 12501-45-0 | Molybic acid (85%) | pdf_6a8faacca882a39304796eef402a5436_fecd0ef8dd3f28f0a739c89160abddfc7410596022594182 |
| AMC | AMMONIUM CHLORIDE | 氯化铵 | 12125-02-9 |  | pdf_6a8faacca882a39304796eef402a5436_f2c6d8292324a47ef4305431e8e59c447410596022594182 |
| AMD | AMMONIUM DICHROMATE | 重铬酸铵 | 7789-09-5 |  | pdf_6a8faacca882a39304796eef402a5436_236870fb0e6ab639eed8b594bf60be2d7410596022594182 |
| AMF | AMMONIUM SULFITE | 亚硫酸铵 | 10196-04-0 |  | pdf_6a8faacca882a39304796eef402a5436_b9d2ba0790732e4ec40fc43f484cf71c7410596022594182 |
| AMH | AMMONIUM HYDROXIDE (<28% AQUEOUS AMMONIA) | 氨水（<28%） | 1336-21-6 |  | pdf_6a8faacca882a39304796eef402a5436_40f40eaeaad41900445f5314ccf24b6b7410596022594182 |
| AMK | N-AMYL METHYL KETONE | 甲基正戊酮 | 110-43-0 |  | pdf_6a8faacca882a39304796eef402a5436_2ebbf54ff04e644bd2d2328d53a529077410596022594182 |
| AMM | N-AMYL MERCAPTAN | 正戊硫醇 | 110-66-7 |  | pdf_6a8faacca882a39304796eef402a5436_316e1b67eb4b0f53df33729ced88b4827410596022594182 |
| AMN | AMMONIUM NITRATE | 硝酸铵 | 6484-52-2 | Nitram | pdf_6a8faacca882a39304796eef402a5436_26488dfa41c33ed2e799f5ca00ad3fb27410596022594182 |
| AMP | AMMONIUM PERCHLORATE | 高氯酸铵 | 7790-98-9 |  | pdf_6a8faacca882a39304796eef402a5436_91d7c7a50278fd300c851185812a0b6c7410596022594182 |
| AMR | AMMONIUM STEARATE | 硬脂酸铵 | 1002-89-7 | Ammonium stearate dispersionSoapStearic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_692a6b851ab25464b3f721f8597cb3f27410596022594182 |
| AMS | AMMONIUM SULFATE | 硫酸铵 | 7783-20-2 |  | pdf_6a8faacca882a39304796eef402a5436_a098a5b9b039810817e3a6af561daf3f7410596022594182 |
| AMT | AMMONIUM THIOCYANATE | 硫氰酸铵 | 1762-95-4 |  | pdf_6a8faacca882a39304796eef402a5436_dda8e6ecbf740dba26ab5028bb6b37297410596022594182 |
| AMY | N-AMYL CHLORIDE | 正戊基氯 | 543-59-9 |  | pdf_6a8faacca882a39304796eef402a5436_e796cb2e68a938bafd012263b4b747897410596022594182 |
| ANB | AMMONIUM BROMIDE | 溴化铵 | 12124-97-9 | Hydrobromic acidmonoammoniate | pdf_6a8faacca882a39304796eef402a5436_2557cd839b20baf97f90494b4925aaf17410596022594182 |
| ANI | ISO-AMYL NITRITE | 亚硝酸异戊酯 | 110-46-3 |  | pdf_6a8faacca882a39304796eef402a5436_8917c391218cef29fefc11689719eb1c7410596022594182 |
| ANL | ANILINE | 苯胺 | 62-53-3 |  | pdf_6a8faacca882a39304796eef402a5436_6b192e1a852fa8115af7759504caf4847410596022594182 |
| ANP | AMMONIUM NITRATE-PHOSPHATE MIXTURE | 硝酸铵-磷酸盐混合物 | 57608-40-9 |  | pdf_6a8faacca882a39304796eef402a5436_d26a94664d09b328b6badf4b204853e87410596022594182 |
| ANS | AMMONIUM NITRATE-SULFATE MIXTURE | 硝酸铵-硫酸盐混合物 |  | Mixed fertilizers | pdf_6a8faacca882a39304796eef402a5436_f017151fa96e6fb9ea7ede92cdd0a79b7410596022594182 |
| ANT | N-AMYL NITR | 硝酸正戊酯 |  | Diesel ignition improperMixed primary amyl nitrates | pdf_6a8faacca882a39304796eef402a5436_fa386d4d758fc26a212845f066a431e87410596022594182 |
| ANU | AMMONIUM NITRATE-UREA SOLUTION | 硝酸铵-尿素溶液 |  | Nitrex nitrogen solutions (non-pressure)Solar nitrogen solutions | pdf_6a8faacca882a39304796eef402a5436_0de28243aeed5c5c4ea387d1877385de7410596022594182 |
| AOL | AMMONIUM OLEATE | 油酸铵 | 544-60-5 | Ammonia soapOleic acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_cbe6c004793384386afa328ac6de2d977410596022594182 |
| AOX | AMMONIUM OXALATE | 草酸铵 | 1113-38-8 | Ammonium oxolateDiamronium oxalateOxalic acid, diammonium salt | pdf_6a8faacca882a39304796eef402a5436_c65aab3c68d7740fdce88b1a86f0191c7410596022594182 |
| APB | AMMONIUM PENTABORATE | 五硼酸铵 | 12007-89-5 | Ammonium decarabateoctahydrateAmmonium pentaboratetrahydrate | pdf_6a8faacca882a39304796eef402a5436_a3da91f14505b59df39d93b59e8bf2f37410596022594182 |
| APC | ANTIMONY PENTACHLORIDE | 五氯化锑 | 7647-18-9 | Antimony (V) chlorideAntimony perchloride | pdf_6a8faacca882a39304796eef402a5436_48db64202c7a0e86fa3f9fc1e7e5337c7410596022594182 |
| APE | AMMONIUM PERSULFATE | 过硫酸铵 | 7727-54-0 | Ammonium peroxydisulfatePeroxydisulfuric acid,diamronium salt | pdf_6a8faacca882a39304796eef402a5436_a4aef0ff70361088b044f90d0d1b76ce7410596022594182 |
| APF | ANTIMONY PENTAFLUORIDE | 五氟化锑 | 7783-70-2 |  | pdf_6a8faacca882a39304796eef402a5436_c2e5df72dd73dfe97de8d6e5c29b0e107410596022594182 |
| APH | ALUMINUM PHOSPHIDE | 磷化铝 | 20859-73-8 | AIPAluminum monophosphide | pdf_6a8faacca882a39304796eef402a5436_be47c8271a9dc1cd53d3a027f1c6d1d87410596022594182 |
| API | AMMONIUM PICRATE, WET | 苦味酸铵（含水） | 131-74-8 |  | pdf_6a8faacca882a39304796eef402a5436_23e4c9dbcf455c9e286ba69ab07439c87410596022594182 |
| APO | ARSENIC PENTAOXIDE | 五氧化二砷 | 1303-28-2 | Arsenic acid anhydrideArsenic oxideArsenic pentoxide | pdf_6a8faacca882a39304796eef402a5436_d0ead5513a59ddb9b207cecfbe8bf1de7410596022594182 |
| APP | AMMONIUM PHOSPHATE | 磷酸铵 | 7783-28-0 |  | pdf_6a8faacca882a39304796eef402a5436_85374637a4091de1d3fde7c7fc60dd4e7410596022594182 |
| APR | 2-AMINO-2-METHYL-1-PROPANOL (90% OR LESS) | 2-氨基-2-甲基-1-丙醇（≤90%） | 124-68-5 |  | pdf_6a8faacca882a39304796eef402a5436_1e69debc024386c7d3db40ad1fd8f1967410596022594182 |
| APS | ACETYL PEROXIDE SOLUTION | 过氧化乙酰溶液 | 110-22-5 | Diacetyl peroxide solution | pdf_6a8faacca882a39304796eef402a5436_c6b3961011d1900049c48ee1314d4f267410596022594182 |
| APT | ANTIMONY POTASSIUM TARTRATE | 酒石酸锑钾 | 28300-74-5 |  | pdf_6a8faacca882a39304796eef402a5436_f8c97648d6d3e2d6261c5e8f1ea792037410596022594182 |
| APY | 4-AMINOPYRIDINE | 4-氨基吡啶 | 504-24-5 | p-AminopyridineAvlrol4-Pyridamine4-Pyridylamine | pdf_6a8faacca882a39304796eef402a5436_0d07724718de68d33aa05d0798d375537410596022594182 |
| ARD | ARSENIC DISULFIDE | 二硫化二砷 | 56320-22-0 |  | pdf_6a8faacca882a39304796eef402a5436_b3d11b58ae0196b8fbddadc8250bb1f07410596022594182 |
| ARF | ASPHALT BLENDING STOCKS: ROOFERS FLUX | 沥青调合料（屋面） |  |  | pdf_6a8faacca882a39304796eef402a5436_a79069539416728c2464485da89fb7867410596022594182 |
| ARL | ACROLEIN | 丙烯醛 | 107-02-8 |  | pdf_6a8faacca882a39304796eef402a5436_d3140d60870cc887c728c6520973be877410596022594182 |
| ART | ARSENIC TRISULFIDE | 三硫化二砷 | 1303-33-9 | Arsenic yellowKing&#x27 s yellowKing&#x27 s yellowOrpimentYellow arsenic suffide | pdf_6a8faacca882a39304796eef402a5436_dd5147e14df82f0a4917740662c8020c7410596022594182 |
| ARX | ARSENIC | 砷 | 7440-38-2 |  | pdf_6a8faacca882a39304796eef402a5436_f99d08380c47f4a68074843dc30510da7410596022594182 |
| ASA | ARSENIC ACID | 砷酸 | 7778-39-4 | Orthoarseric acid | pdf_6a8faacca882a39304796eef402a5436_7e6e7290a5ac017317d5ab63e17625337410596022594182 |
| ASC | ANISOYL CHLORIDE | 茴香酰氯 | 100-07-2 | p-Anosyl chloride | pdf_6a8faacca882a39304796eef402a5436_2dce9de3627e9fafcf8f3660bf8fc1f17410596022594182 |
| ASF | AMMONIUM SULFIDE | 硫化铵 | 12135-76-1 | Ammonton hydrogen sulfidesolutionAmmonium sulfhyrate solutionAmmonium sulfide so | pdf_6a8faacca882a39304796eef402a5436_a227a6662ad5aafc03ce0a81d73b3b427410596022594182 |
| ASL | AMMONIUM SILICOFLUORIDE | 氟硅酸铵 | 16919-19-0 | Ammonium fluorosilicate | pdf_6a8faacca882a39304796eef402a5436_c26c51ca61ef973d74407fee9883ed1b7410596022594182 |
| ASM | AMMONIUM SULFAMATE | 氨基磺酸铵 | 7773-06-0 |  | pdf_6a8faacca882a39304796eef402a5436_59dbf3c10698ffdbc0729f0a7d78f62a7410596022594182 |
| ASP | ASPHALT | 沥青 |  | Asphalt commentsAsphalt bitumenBlitumenPetroleum asphalt | pdf_6a8faacca882a39304796eef402a5436_65f29ecb10214a7ef2f2d36232f50a897410596022594182 |
| ASR | ASPHALT BLENDING STOCKS: STRAIGHT RUN RESIDUE | 沥青调合料（直馏残渣） |  | Carpeting mediumPetroleum pitchPetroleum residueResidual asphaltRoad binderSeal- | pdf_6a8faacca882a39304796eef402a5436_9391c72a0a2cfbcd0f022a86145c68747410596022594182 |
| AST | ARSENIC TRICHLORIDE | 三氯化砷 | 7784-34-1 | Arsenic chlorideArsenic chlorideArsenic chlorideButter of arsenicCaustic arsenic | pdf_6a8faacca882a39304796eef402a5436_fed83530550ff5287b8f3bcaa1de65e67410596022594182 |
| ASU | AMMONIUM BISULFITE | 亚硫酸氢铵 | 10192-30-0 | Ammonium hydrogen sulfiteAmmonium hydrosulfteAmmonium monosulfite | pdf_6a8faacca882a39304796eef402a5436_b3d005c8de5b7fbe02ef5b17451069fe7410596022594182 |
| ASX | ALUMINUM SULFATE SOLUTION | 硫酸铝溶液 | 10043-01-3 |  | pdf_6a8faacca882a39304796eef402a5436_c4b12fa105e1fcd8c6ce0d3d220aec2c7410596022594182 |
| ATA | ACETYLACETONE | 乙酰丙酮 | 123-54-6 | 2,4-Pentanedione | pdf_6a8faacca882a39304796eef402a5436_cc79dbae5c8b86071071761fbf0d3d697410596022594182 |
| ATB | ANTIMONY TRIBROMIDE | 三溴化锑 | 7789-61-9 | Antimonous bromide | pdf_6a8faacca882a39304796eef402a5436_7687f464ec3821cee6159e867fc83b097410596022594182 |
| ATC | ALLYLTRICHLOROSILANE | 烯丙基三氯硅烷 | 107-37-9 | Allytsilicone trichloride | pdf_6a8faacca882a39304796eef402a5436_fdf36126bae8fe58532b0de3553e0b687410596022594182 |
| ATF | AMMONIUM THIOSULFATE | 硫代硫酸铵 | 7783-18-8 | Ammonium hyposulfite | pdf_6a8faacca882a39304796eef402a5436_5dfbe43c7d0ed9f2b3c1e70d336607f57410596022594182 |
| ATH | ANTHRACENE | 蒽 | 120-12-7 |  | pdf_6a8faacca882a39304796eef402a5436_662d7d433a876816cbf5eddd07f2a40e7410596022594182 |
| ATL | AMYL PHTHALATE | 邻苯二甲酸戊酯 | 131-18-0 |  | pdf_6a8faacca882a39304796eef402a5436_83afbc732f9b0e6ea01d9fd435b8e9b47410596022594182 |
| ATM | ANTIMONY TRICHLORIDE | 三氯化锑 | 10025-91-9 | Antimony (iii) chlorideButter of antimony | pdf_6a8faacca882a39304796eef402a5436_f74b44ced5358ee2ea396b8ede2838977410596022594182 |
| ATN | ACETONITRILE | 乙腈 | 75-05-8 |  | pdf_6a8faacca882a39304796eef402a5436_92b4d572488676067134775b73590d177410596022594182 |
| ATO | ARSENIC TRIOXIDE | 三氧化二砷 | 1327-53-3 | Arsenus sesquioxideArsenus acidArsenus acid anhydrideArsenus oxideWhite arsenic | pdf_6a8faacca882a39304796eef402a5436_75af129863c0a82c65d9efc8f90963a57410596022594182 |
| ATR | AMMONIUM TARTRATE | 酒石酸铵 | 3164-29-2 | 1-Tartarc acid, ammonium salt | pdf_6a8faacca882a39304796eef402a5436_aee2c70e293044d7f549e7f3e4f117bc7410596022594182 |
| ATS | N-AMYLTRICHLOROSILANE | 戊基三氯硅烷 | 107-72-2 | Pentysilicon trichlorideTrichloroamsilianeTrichloropentyiliane | pdf_6a8faacca882a39304796eef402a5436_ccaeda0caabcfdd61e94b476096374bc7410596022594182 |
| ATT | ANTIMONY TRIFLUORIDE | 三氟化锑 | 7783-56-4 |  | pdf_6a8faacca882a39304796eef402a5436_e1b393ad28420ebdf23031c256b8e4be7410596022594182 |
| ATV | AMMONIUM THIOSULFATE SOLUTION (60% OR LESS) | 硫代硫酸铵溶液（≤60%） | 7783-18-8 |  | pdf_6a8faacca882a39304796eef402a5436_f379dd6f634386f31d9bcc8a390bb3d77410596022594182 |
| ATX | ANTIMONY TRIOXIDE | 三氧化二锑 | 1309-64-4 |  | pdf_6a8faacca882a39304796eef402a5436_aeaa4c4a6152d1e033574d2e47e61c817410596022594182 |
| ATZ | ATRAZINE | 莠去津 | 1912-24-9 |  | pdf_6a8faacca882a39304796eef402a5436_813822e112c7dbc0639fb92d16b1f6177410596022594182 |
| AYA | TERT-AMYL ACETATE | 乙酸叔戊酯 | 625-16-1 | tert-Pentyl acetate | pdf_6a8faacca882a39304796eef402a5436_04c7a1989b09f5b2287af2561d86c5ee7410596022594182 |
| AZM | AZINPHOS METHYL | 甲基谷硫磷 | 86-50-0 | O,O-Dimethyl s-(4-oxo-1,2,3-benzotrazine-3-(4h)-ylmethylphosphorothidhoateGusath | pdf_6a8faacca882a39304796eef402a5436_300e6962d6f643373d30cf9de4602f6f7410596022594182 |
| BAB | BROMOACETYL BROMIDE | 溴乙酰溴 | 598-21-0 | Bromoethanoyl bromide | pdf_6a8faacca882a39304796eef402a5436_7dca77f89955cb8a635cdf3ba73a707e7410596022594182 |
| BAC | BORIC ACID | 硼酸 | 10043-35-3 | Boracic acidOrthoboric acid | pdf_6a8faacca882a39304796eef402a5436_952b88b3436bc88683f7435a138dcc527410596022594182 |
| BAD | ISO-BUTYRALDEHYDE | 异丁醛 | 78-84-2 |  | pdf_6a8faacca882a39304796eef402a5436_3f79d3dadde572e114e2384e65dea9717410596022594182 |
| BAI | ISO-BUTYL ACRYLATEBAl | 丙烯酸异丁酯 |  | Acrylic acid, isobuly ester isobuly1-2propenoate | pdf_6a8faacca882a39304796eef402a5436_f2ba363c5c035f301115c894f3aba0397410596022594182 |
| BAL | BENZYL ALCOHOL | 苄醇 | 100-51-6 | Benzenecarbinolalpha-HydroxytoluenenePhenyimethanolPhenyimethyl alcohol | pdf_6a8faacca882a39304796eef402a5436_f8cd63f91eb52e55af12a6674c39a20e7410596022594182 |
| BAM | N-BUTYLAMINE | 正丁胺 | 109-73-9 |  | pdf_6a8faacca882a39304796eef402a5436_982ccbc77db9674fb749524177863ab27410596022594182 |
| BAN | N-BUTYL ALCOHOL | 正丁醇 | 71-36-3 |  | pdf_6a8faacca882a39304796eef402a5436_9cf3848a8c159b9865e036f5f8b842c57410596022594182 |
| BAS | SEC-BUTYL ALCOHOL | 仲丁醇 | 78-92-2 |  | pdf_6a8faacca882a39304796eef402a5436_e26b9e8086c4b01f83727b05e29fa1f97410596022594182 |
| BAT | TERT-BUTYL ALCOHOL | 叔丁醇 | 75-65-0 | 2-Methyl-2-propanolTrimethylcarbinol | pdf_6a8faacca882a39304796eef402a5436_ba61b3e8826a2749b40f45661f91001f7410596022594182 |
| BBR | BENZYL BROMIDE | 苄基溴 | 100-39-0 |  | pdf_6a8faacca882a39304796eef402a5436_a64e8560c9aaa902d6fb5dc26d655f507410596022594182 |
| BBT | 2-BROMOBUTANE | 2-溴丁烷 | 78-76-2 | sec-Butyl bromideMethyl ethyl bromo-methane | pdf_6a8faacca882a39304796eef402a5436_6cfbd8d541c3f828854793e2a29cd0027410596022594182 |
| BBU | 1-BROMOBUTANE | 1-溴丁烷 | 109-65-9 | n-BromobulaneButyl bromblen-Butyl brombide | pdf_6a8faacca882a39304796eef402a5436_ae22a379244439f9084ca42d30e43cb27410596022594182 |
| BBZ | BROMOBENZENE | 溴苯 | 108-86-1 | Bromobenzal Monbromobenzene Phenyl bromide | pdf_6a8faacca882a39304796eef402a5436_1d0f5cd7de135e1d1cad4c2fd911c1627410596022594182 |
| BCF | BENZYL CHLOROFORMATE | 氯甲酸苄酯 | 501-53-1 | Benzycarbonyl chloride Benzy chlorocarbonate Carobenzoxy chloride Chloroformic a | pdf_6a8faacca882a39304796eef402a5436_e53ffb85a13d84f3baa61366eaf5b6b07410596022594182 |
| BCL | BENZYL CHLORIDE | 苄基氯 | 100-44-7 | alpha-Chlorotolueneomega-Chlorotoluene | pdf_6a8faacca882a39304796eef402a5436_ca3c5b353b26fa0382cdeb55a66662c17410596022594182 |
| BCN | N-BUTYL ACETATE | 乙酸正丁酯 | 123-86-4 | Acetic acid, n-butyl esterButyl acetateButyl ethanoate | pdf_6a8faacca882a39304796eef402a5436_c740cc4507f99db15d852dcad3e65ffa7410596022594182 |
| BCP | BOILER COMPOUND, LIQ | 锅炉水处理剂（液体） |  | Akaway liquid alkaline deruster | pdf_6a8faacca882a39304796eef402a5436_971c156687bdb6844d18a3c2bb4fa8697410596022594182 |
| BCR | BARIUM CHLORATE | 氯酸钡 | 13477-00-4 | Barium chlorate monohydrate | pdf_6a8faacca882a39304796eef402a5436_4a89a4baaf58e21fb93b97c9e9f03ff67410596022594182 |
| BCS | BUTYLTRICHLOROSILANE | 丁基三氯硅烷 | 7521-80-4 | n-Butytrichorosilane | pdf_6a8faacca882a39304796eef402a5436_bfe436f8b5c3b19e95181f0cd49d9ad97410596022594182 |
| BCY | BARIUM CYANIDE | 氰化钡 |  | Barium cyanide solid | pdf_6a8faacca882a39304796eef402a5436_2f56644cd4a8d0c589c1f0d27bbde7517410596022594182 |
| BDE | BISPHENOL A DIGLYCIDYL ETHER | 双酚A二缩水甘油醚 | 1675-54-3 |  | pdf_6a8faacca882a39304796eef402a5436_7a0845b3e397487ea38f407cd26c0ba07410596022594182 |
| BDI | BUTADIENE | 丁二烯 | 106-99-0 |  | pdf_6a8faacca882a39304796eef402a5436_f05e88d2665b255e65961d86abaf6f087410596022594182 |
| BDM | BENZYL DIMETHYLAMINE | 苄基二甲胺 |  | Catalyst 9915a-(Dimethylamino) loluenAN-Dimethyl benzemethanaminAN-Dimethyl benz | pdf_6a8faacca882a39304796eef402a5436_2db9274a284604fe739861d9c50495f17410596022594182 |
| BDO | 1,4-BUTANEDIOL | 1,4-丁二醇 | 110-63-4 | 1.4-Bulylene glycol1.4-DihydroxybutaneTetramethylene glycol | pdf_6a8faacca882a39304796eef402a5436_3619136a5d654f252dd9e7184751bf857410596022594182 |
| BEC | BERYLLIUM CHLORIDE | 氯化铍 | 7787-47-5 |  | pdf_6a8faacca882a39304796eef402a5436_c719a66071a9fe978ec8d5aeccbe796d7410596022594182 |
| BEF | BERYLLIUM FLUORIDE | 氟化铍 | 7787-49-7 |  | pdf_6a8faacca882a39304796eef402a5436_2fe0b63b1508916a4153cda056c04f787410596022594182 |
| BEM | BERYLLIUM | 铍 | 7440-41-7 |  | pdf_6a8faacca882a39304796eef402a5436_cc90992a44386647ffc2bb5351e4a3667410596022594182 |
| BEN | BERYLLIUM NITRATE | 硝酸铍 | 13597-99-4 | Beryllium nitrate trihydrate | pdf_6a8faacca882a39304796eef402a5436_bdb1917453a5625bed36e2d334a24f537410596022594182 |
| BEO | BERYLLIUM OXIDE | 氧化铍 | 1304-56-9 | BerylliaBromelle | pdf_6a8faacca882a39304796eef402a5436_cf2e0935bb91cc5c2a5c50a6ab9e9b127410596022594182 |
| BES | BERYLLIUM SULFATE | 硫酸铍 | 13510-49-1 | Beryllium sulfate tetrahydrate | pdf_6a8faacca882a39304796eef402a5436_a935145722e6497fea3e9591498da08e7410596022594182 |
| BFN | N-BUTYL FORMATE | 甲酸正丁酯 | 592-84-7 |  | pdf_6a8faacca882a39304796eef402a5436_906ca0def6548959be56d81f28e5e37d7410596022594182 |
| BFO | N-BUTYL CHLOROFORMATE | 氯甲酸正丁酯 | 592-34-7 | n-Butyl chlorocarbonateCarbonchloridic acid, butylesterChlorocarbonic acid, n-bu | pdf_6a8faacca882a39304796eef402a5436_f777bd8df85a95854a1f867aaa82cefd7410596022594182 |
| BGE | N-BUTYL GLYCIDYL ETHER | 正丁基缩水甘油醚 | 2426-08-6 | 1-Butoxy-2,3-epoxypropane1,2-Epoxy-3-butoxypropane2,3-Epoxypropyl butyl ether | pdf_6a8faacca882a39304796eef402a5436_1b202d96349d64af576dda46777a7d227410596022594182 |
| BHC | GAMMA-BENZENE HEXACHLORIDE | γ-六氯环己烷（林丹） | 27154-44-5 |  | pdf_6a8faacca882a39304796eef402a5436_fb6dc96cb6e04e8d15f47e1315f462ea7410596022594182 |
| BHP | TERT-BUTYL HYDROPEROXIDE | 叔丁基过氧化氢 | 75-91-2 | Cadox TBH | pdf_6a8faacca882a39304796eef402a5436_248330e77bbbb7e747ea1e2d72be4be67410596022594182 |
| BIB | ISOBUTYL ISOBUTYRATE | 异丁酸异丁酯 | 97-85-8 |  | pdf_6a8faacca882a39304796eef402a5436_f264fd0dcd0a7f1014aa1685bc5124ce7410596022594182 |
| BLE | BUTYL LACTATE | 乳酸丁酯 | 138-22-7 | Butyl a-hydroxypropionate | pdf_6a8faacca882a39304796eef402a5436_35b6a945b8dd2a55283071c1000b49897410596022594182 |
| BMA | BENZYLTRIMETHYLAMMONIUM CHLORIDE | 苄基三甲基氯化铵 | 56-93-9 | BTMACTrimhyberbenzylammoniumchloride | pdf_6a8faacca882a39304796eef402a5436_e7782e58bf103e6d5dc66c98f74f72fb7410596022594182 |
| BMI | ISOBUTYL METHACRYLATE | 甲基丙烯酸异丁酯 | 97-86-9 | Isobutyl alpha-methacrylateIsobutyl 2-methyl-2-propenateMethacrylic acid, isobut | pdf_6a8faacca882a39304796eef402a5436_3ac3d8fa90559b3e543512bfe01686937410596022594182 |
| BMN | N-BUTYL METHACRYLATE | 甲基丙烯酸正丁酯 | 97-88-1 |  | pdf_6a8faacca882a39304796eef402a5436_f4ea6f514dec2bdf2e3434865e110cfd7410596022594182 |
| BNI | BUTYRONITRILE | 丁腈 | 109-74-0 | ButanenitrileButryric acid nitrileCyanopropanePropyl cyanide | pdf_6a8faacca882a39304796eef402a5436_63d345c3511389a32f002f444ba2d5a07410596022594182 |
| BNP | 2-BUTANONE PEROXIDE | 丁酮过氧化物 | 1338-23-4 | 2-Butanone, peroxideButanox M50, M105, LPTChaloxyd MEKP-ha 1, -la 1Ethylmethylke | pdf_6a8faacca882a39304796eef402a5436_39e45454adc999b8a8aedc0e7425f4b67410596022594182 |
| BNT | BARIUM NITRATE | 硝酸钡 | 10022-31-8 |  | pdf_6a8faacca882a39304796eef402a5436_5b2bae4e02f8c04bb9e7edf8abc942a77410596022594182 |
| BNZ | BENZENE | 苯 | 71-43-2 | BenzolBenzole | pdf_6a8faacca882a39304796eef402a5436_39b989a341ec1e9275724f731fcb6dd57410596022594182 |
| BOC | BISMUTH OXYCHLORIDE | 氯氧化铋 | 7787-59-9 |  | pdf_6a8faacca882a39304796eef402a5436_512c99eb132f39632d9351106b887d987410596022594182 |
| BPA | BISPHENOL A | 双酚A | 80-05-7 | p.p.D.Dihydroxydiphenyldimethylmethane 2.2-Bis(4-Hydroxphenyl)propane 4.4&#x27 - | pdf_6a8faacca882a39304796eef402a5436_6db7b7688c4a80cbfb97a1d94ea8df4d7410596022594182 |
| BPC | BARIUM PERCHORATE | 高氯酸钡 | 13465-95-7 | Barium perchlorate trihydrate | pdf_6a8faacca882a39304796eef402a5436_692e6f7af05ad15d21991b4c8f7a26ed7410596022594182 |
| BPD | BENZENE PHOSPHORUS DICHLORIDE | 苯基二氯化膦 | 644-97-3 | DichlorophenylphosphinePheny/phosphone dichloridePheny/phosphonone dichloridePhe | pdf_6a8faacca882a39304796eef402a5436_8fef060b64a556c110dfa453ebf000fb7410596022594182 |
| BPE | 2-BROMOPENTANE | 2-溴戊烷 | 107-81-3 | 2-Pentybromide | pdf_6a8faacca882a39304796eef402a5436_703e8e4776eefc884a84e845531aa6b87410596022594182 |
| BPF | BROMINE PENTAFLUORIDE | 五氟化溴 | 7789-30-2 |  | pdf_6a8faacca882a39304796eef402a5436_5fb11af1c1516d6c194969c4f1d4f1067410596022594182 |
| BPH | BUTYL BENZYL PHTHALATE | 邻苯二甲酸丁苄酯 | 85-68-7 | Benzyl n-butyl phthalatePhthalic acid, benzyl butyl ether | pdf_6a8faacca882a39304796eef402a5436_f54791094c8f20ed391de639201121b57410596022594182 |
| BPM | BARIUM PERMANGANATE | 高锰酸钡 | 7787-36-2 |  | pdf_6a8faacca882a39304796eef402a5436_15b83324e564faa27d5a3c308edd71217410596022594182 |
| BPN | N-BUTYL PROPIONATE | 丙酸正丁酯 | 590-01-2 | Propanonic acid bulyl esterProponic acid butyl ester | pdf_6a8faacca882a39304796eef402a5436_50c8b4bea676e1c231e2f344c94bb2d97410596022594182 |
| BPO | BARIUM PEROXIDE | 过氧化钡 | 1304-29-6 | Barium binoxideBarium dioxideBarium superoxide | pdf_6a8faacca882a39304796eef402a5436_c799e0f32cf2aed12c7626e7ffc53c5b7410596022594182 |
| BPR | 1-BROMOPROPANE | 1-溴丙烷 | 106-94-5 | Propylbromiden-Propylbromide | pdf_6a8faacca882a39304796eef402a5436_4a6fc37034d704625b9f93f76ae16c8f7410596022594182 |
| BPT | BENZENE PHOSPHORUS THIODICHLORIDE | 苯基硫代二氯化膦 | 3497-00-5 | Benzenethiophosphony chloridePheny/phosphonethiodichloridedichloride | pdf_6a8faacca882a39304796eef402a5436_8673ad3be18f6f2019592ea0fd9db43c7410596022594182 |
| BRA | N-BUTYRIC ACID | 正丁酸 | 107-92-6 | Butanic acidButanic acidButryic acidEthylacetic acidPropanecarboxylic acid | pdf_6a8faacca882a39304796eef402a5436_281f5b277ab826bf912be81dd3a92a1b7410596022594182 |
| BRC | BARIUM CARBONATE | 碳酸钡 | 513-77-9 |  | pdf_6a8faacca882a39304796eef402a5436_b0de3afbdff62b91e57de92bcacf267b7410596022594182 |
| BRE | BROMOACETONE | 溴丙酮 | 598-31-2 | Acetoryl bromideAcetoryl methylbromideBromomethyl methyl ketone1-Bromo-2-propano | pdf_6a8faacca882a39304796eef402a5436_f222736f183bc32b961038094e8327877410596022594182 |
| BRO | BROMOFORM | 三溴甲烷（溴仿） | 75-25-2 | Formyl tribromideMethane, tribromodeMethylene tribromideMethyl tribromide | pdf_6a8faacca882a39304796eef402a5436_c5cda77e91e1a907d772d1f8f0fe2c5b7410596022594182 |
| BRT | BORON TRICHLIORIDE | 三氯化硼 |  | Boron chloride | pdf_6a8faacca882a39304796eef402a5436_47aa4c7c3090e6bb55e1dfc321f1617d7410596022594182 |
| BRU | BRUCINE | 马钱子碱 | 357-57-3 | (-)Brucine dihydrolate 10,11-Dimethoxystrychnine | pdf_6a8faacca882a39304796eef402a5436_c4aa5f81427f696c9afd5c6830efb5f37410596022594182 |
| BRX | BROMINE | 溴 | 7726-95-6 |  | pdf_6a8faacca882a39304796eef402a5436_66d094a5c880299c26a788ad6dcfc0fa7410596022594182 |
| BSC | BENZENESULFONYL CHLORIDE | 苯磺酰氯 | 98-09-9 |  | pdf_6a8faacca882a39304796eef402a5436_520831020afe4c962c933ade88e379967410596022594182 |
| BTA | SEC-BUTYL ACETATE | 乙酸仲丁酯 | 105-46-4 | Acetic acid, sec-butyl ester | pdf_6a8faacca882a39304796eef402a5436_003caabddb051f096c5d8f926464eca57410596022594182 |
| BTB | BORON TRIBROMIDE | 三溴化硼 | 10294-33-4 |  | pdf_6a8faacca882a39304796eef402a5436_ca8d81f9d44ae2dff8269a4bb1ad31ad7410596022594182 |
| BTC | N-BUTYL ACRYLATE | 丙烯酸正丁酯 | 141-32-2 | Acryclic acid, -butyl esterButyl acrylaten-Butyl 2-propenoate | pdf_6a8faacca882a39304796eef402a5436_5cbc2fabece6e72d74ae356ce0ce13c27410596022594182 |
| BTD | 1,4-BUTYNEDIOL | 1,4-丁炔二醇 | 110-65-6 | 2-Butyne-1, 4-dicol1, 1.4-Dihydroxy-2-butyne | pdf_6a8faacca882a39304796eef402a5436_79fcb390551512c7584eba705f470cf77410596022594182 |
| BTF | BROMINE TRIFLUORIDE | 三氟化溴 | 7787-71-5 |  | pdf_6a8faacca882a39304796eef402a5436_9b1cabe9a4e2901ccd13eb96f82d81767410596022594182 |
| BTL | SEC-BUTYLAMINE | 仲丁胺 | 13952-84-6 |  | pdf_6a8faacca882a39304796eef402a5436_9e00da6d4387aec2d9b7164ac194f8367410596022594182 |
| BTM | N-BUTYL MERCAPTAN | 正丁硫醇 | 109-79-5 | 1-ButanethilThiobutyl alcohol | pdf_6a8faacca882a39304796eef402a5436_bf5ed579c7e8c5415e4e02fc5cb1d1037410596022594182 |
| BTN | BUTYLENE | 丁烯 |  | 1-Butene | pdf_6a8faacca882a39304796eef402a5436_9ce1f7bd181c4cac1df559fb1c69c5887410596022594182 |
| BTO | 1,2-BUTYLENE OXIDE | 1,2-环氧丁烷 | 106-88-7 |  | pdf_6a8faacca882a39304796eef402a5436_e905f7eaf20bc06a45a8db5450e721ac7410596022594182 |
| BTP | P-TERT-BUTYLPHENOL | 对叔丁基苯酚 | 98-54-4 |  | pdf_6a8faacca882a39304796eef402a5436_eeac879fd3ed6740c5937f76e722a41b7410596022594182 |
| BTR | N-BUTYRALDEHYDE | 正丁醛 | 123-72-8 | ButaldehydeButanalButylaldehydeButyl aldehydeButyraldehydeButyraldehyde | pdf_6a8faacca882a39304796eef402a5436_af68818c4466569f75827598e3abb7867410596022594182 |
| BUA | TERT-BUTYLAMINE | 叔丁胺 | 75-64-9 | 2-Aminoisobulane2-Amino-2-methylpropane1.1-DimethyltylamineTBATrimethylaminometh | pdf_6a8faacca882a39304796eef402a5436_a3c0d95aed00f84995aada524b530ba67410596022594182 |
| BUB | BUTYL BUTYRATE | 丁酸丁酯 | 109-21-7 | Butanic acid, butyl esterButyl butanicateButylric acid, butyl ester | pdf_6a8faacca882a39304796eef402a5436_1d1cabc9920a3c820a54806672b17f087410596022594182 |
| BUC | BUTYRYL CHLORIDE | 丁酰氯 | 141-75-3 | Butanoly chlorideButoyl chloriden-Butyryl chloride | pdf_6a8faacca882a39304796eef402a5436_f1bebee15edf5b7e5ff73a6467c427f77410596022594182 |
| BUD | 1,4-BUTENEDIOL | 1,4-丁烯二醇 | 821-11-4 | 2-Butene-1, 4-diolcis-2-Butene-1, 4-diol1, 4-Dihydroxy-2-butene | pdf_6a8faacca882a39304796eef402a5436_2095817fe7deaa4ab047b64ad30774e47410596022594182 |
| BUE | BUTYL TOLUENE | 丁基甲苯 |  | 4-tert-Butyloluenep-tert-Butyloluenen-Methyl-tert-butylbenzene1-Methyl-4-tert-bu | pdf_6a8faacca882a39304796eef402a5436_7f1d83e3527a10631a2fc428925772af7410596022594182 |
| BUF | N-VALERALDEHYDE | 正戊醛 | 110-62-3 |  | pdf_6a8faacca882a39304796eef402a5436_04a69cc8c632a50f981a3312b3a0622c7410596022594182 |
| BUG | BUTYLENE GLYCOL | 丁二醇 | 107-88-0 | ButanediolDihydroxybutane | pdf_6a8faacca882a39304796eef402a5436_f21c8e3eee216eb3c8619fde2886b83a7410596022594182 |
| BUT | BUTANE | 丁烷 | 106-97-8 | n-Butane | pdf_6a8faacca882a39304796eef402a5436_4c3707ac2c97b31b7014dd8a009775397410596022594182 |
| BYA | TERT-BUTYL ACETATE | 乙酸叔丁酯 | 540-88-5 | Acetic acid, ter-butyl ester | pdf_6a8faacca882a39304796eef402a5436_15fac960c51efcf915023933c7522ccd7410596022594182 |
| BYC | BUTYL CHLORIDE | 丁基氯 | 109-69-3 |  | pdf_6a8faacca882a39304796eef402a5436_4d6ebcbdf15824ec5d08bb6a28b770ae7410596022594182 |
| BZA | BENZOIC ACID | 苯甲酸 | 65-85-0 | Benzenecarboxylic acidCarboxybenzenedracyclic acid | pdf_6a8faacca882a39304796eef402a5436_0ccc052663a9c3bd4c15e633d4b0b0f27410596022594182 |
| BZC | BENZOYL CHLORIDE | 苯甲酰氯 | 98-88-4 | Benzenecarbonyl chloride | pdf_6a8faacca882a39304796eef402a5436_e564333ef95da41f1986217da1fe15557410596022594182 |
| BZD | BENZALDEHYDE | 苯甲醛 | 100-52-7 | Benzic aldehydeOil of bitter almond | pdf_6a8faacca882a39304796eef402a5436_707f5025a44d000221881c768faed5107410596022594182 |
| BZE | BENZYL ACETATE | 乙酸苄酯 | 140-11-4 | Acetic acid, phenylmethyl esteralpha-AcetoxytolueneAcetic acid, benzyl esterBeno | pdf_6a8faacca882a39304796eef402a5436_c3063022c1c6e693a5b51e4b2bf03d6e7410596022594182 |
| BZI | BENZIDINEBZl | 联苯胺 |  | p.p.-Bianline (1,1&#x27 -Biphenyl)-4,4&#x27 -diamine p.p.-Diaminobiphenyl p-Diam | pdf_6a8faacca882a39304796eef402a5436_6c24096f2eb258bea89e233e1d402d4d7410596022594182 |
| BZL | BENZAL CHLORIDE | 苄叉二氯 | 98-87-3 |  | pdf_6a8faacca882a39304796eef402a5436_1004fdbda3d7a8291f3004477a7fdde77410596022594182 |
| BZM | BENZYLAMINE | 苄胺 | 100-46-9 | alpha-AminotueluenPhenylmethyl amine | pdf_6a8faacca882a39304796eef402a5436_f757a73c7c915b3a0a44badfcc46d5fd7410596022594182 |
| BZN | BENZONITRILE | 苯甲腈 | 100-47-0 | Benzoic acid nitrileCyanobenzenePhenylcyanide | pdf_6a8faacca882a39304796eef402a5436_f2e6430883536dc906fe6f0b41767df07410596022594182 |
| BZO | BENZYLDIMETHYLOCTADECYLAMMONIUM CHLORIDE | 苄基二甲基十八烷基氯化铵 | 122-19-0 | Benzydimethylstearyl ammonium chlorideStearyldimethylbenzylammoniumchlorideTallo | pdf_6a8faacca882a39304796eef402a5436_8a40aa78634b5cadbab709f3de1cf7357410596022594182 |
| BZP | BENZOPHENONE | 二苯甲酮 | 119-61-9 |  | pdf_6a8faacca882a39304796eef402a5436_f48816e1a6766f2c9978055e1e30c4207410596022594182 |
| BZQ | P-BENZOQUINONE | 对苯醌 | 106-51-4 | Benzoquinone1.4-Benzoquinone1.4-Cyclohexadiene2.5-Cyclohexadiene-1,4-dioneQuinon | pdf_6a8faacca882a39304796eef402a5436_823152b42c84a97829fca6bfc524fa847410596022594182 |
| BZT | BENZENETHIOL | 苯硫酚 | 108-98-5 | MercapobenzenePhenyl mercapanPhenyltholThiophenol | pdf_6a8faacca882a39304796eef402a5436_adeca17fbbfec24def001e9ff94c1ee67410596022594182 |
| CAA | COPPER ACETOARSENITE | 乙酰亚砷酸铜（巴黎绿） | 12002-03-8 |  | pdf_6a8faacca882a39304796eef402a5436_0eff9ea83229022cf3a49bbde346ffd47410596022594182 |
| CAC | CHOROACETYL CHLORIDE | 氯乙酰氯 | 79-04-9 | Chloracetyl chloride | pdf_6a8faacca882a39304796eef402a5436_338ab3909871aa7e2b62c8461a1676c57410596022594182 |
| CAF | CALCIUM FLUORIDE | 氟化钙 | 7789-75-5 | FluorsparFluospar | pdf_6a8faacca882a39304796eef402a5436_8cb3989a53b0468a41f921508ba5eead7410596022594182 |
| CAH | CALCIUM HYDROXIDE | 氢氧化钙 | 1305-62-0 | Slaked lime | pdf_6a8faacca882a39304796eef402a5436_dc4dfdfdbbfa38f0e65da52c6434a17f7410596022594182 |
| CAL | CALCIUM PHOSPHATE | 磷酸钙 | 7758-87-4 | Calcium biphosphateCalcium pyrophosphateCalcium superphosphateDCPDicalcium phosp | pdf_6a8faacca882a39304796eef402a5436_776747416bd5eb9514381f5b73b299397410596022594182 |
| CAM | CALCIUM | 钙 | 7440-70-2 |  | pdf_6a8faacca882a39304796eef402a5436_463f6b72c0eb8885a20a255f872ade337410596022594182 |
| CAO | CALCIUM OXIDE | 氧化钙 | 1305-78-8 | QuickimeUnsiaked lime | pdf_6a8faacca882a39304796eef402a5436_314937e69395ab1dfd9bda1eff88f4907410596022594182 |
| CAP | P-CHOROANILINE | 对氯苯胺 | 106-47-8 | 1-Amino-4-chlorobenzene4-Chloroaniline4-Chlorophenylamine | pdf_6a8faacca882a39304796eef402a5436_9553e47796597ad941256e5ed135af0b7410596022594182 |
| CAR | CARENE | 3-蒈烯 | 13466-78-9 | 3-CarensIsodiprene3,7.7-Trimethylbicyclo[0, 1,4]hept-3-ene4,7.7-Trimethyl-3-norc | pdf_6a8faacca882a39304796eef402a5436_fa02d4eb32f17ab1006b5aaacdb250767410596022594182 |
| CAS | CALCIUM ARSENITE | 亚砷酸钙 | 52740-16-6 | Arsenous acid, calcium saltCalcium arsenite sold | pdf_6a8faacca882a39304796eef402a5436_1cb79d79de39d6c819d113f386b1c46a7410596022594182 |
| CAT | CADMIUM ACETATE | 乙酸镉 | 543-90-8 | Cadmium acetate dihydrate | pdf_6a8faacca882a39304796eef402a5436_603ee9a2b9d7d4002890962985f3977b7410596022594182 |
| CBA | COBALT ACETATE | 乙酸钴 | 71-48-7 |  | pdf_6a8faacca882a39304796eef402a5436_81ae6ac862a5516b9b00cf02edca0bd57410596022594182 |
| CBB | CARBON DISULFIDE | 二硫化碳 | 75-15-0 | Carbon bisuflide | pdf_6a8faacca882a39304796eef402a5436_e3bcbfe18dae9adc6d4c3c7a654f14e97410596022594182 |
| CBC | COBALT CHLORIDE | 氯化钴 | 7646-79-9 |  | pdf_6a8faacca882a39304796eef402a5436_3deb50a38bb078b58e279715c98fbbcc7410596022594182 |
| CBD | COPPER BROMIDE (OUS) | 溴化亚铜 |  | Copper monobromide | pdf_6a8faacca882a39304796eef402a5436_23c6e144b6794baebed30a511fced6fd7410596022594182 |
| CBF | CARBOFURAN | 克百威（呋喃丹） | 1563-66-2 |  | pdf_6a8faacca882a39304796eef402a5436_2a2e9d65cc32ce88b3a148ee9019d0887410596022594182 |
| CBN | 4-CHOROBUTYRONITRILE | 4-氯丁腈 | 628-20-6 |  | pdf_6a8faacca882a39304796eef402a5436_557330ec408b63aa858e8baf80117bd27410596022594182 |
| CBO | CARBOLIC OIL (MIXTURE) | 石炭酸油 |  | Carbolic acidLiquefied phenolMiddle oil | pdf_6a8faacca882a39304796eef402a5436_b87227e4636b361573f0fb1b084f2cb07410596022594182 |
| CBR | CYANOGEN BROMIDE | 溴化氰 | 506-68-3 |  | pdf_6a8faacca882a39304796eef402a5436_015967dde1ebfaa5590706a7b6d648517410596022594182 |
| CBS | COBALT SULFATE | 硫酸钴 | 10124-43-3 | BieberteCobaltous sulfate heptahyrateCobalt(II) sulfate | pdf_6a8faacca882a39304796eef402a5436_e28037601c48eddbf3d3318578806cbc7410596022594182 |
| CBT | CARBON TETRACHLORIDE | 四氯化碳 | 56-23-5 |  | pdf_6a8faacca882a39304796eef402a5436_c12f003aab348455a72dc04e0a338c067410596022594182 |
| CBY | CARBARYL | 甲萘威（西维因） | 63-25-2 | 1-Naphthyl n-methylcarbamateSevin | pdf_6a8faacca882a39304796eef402a5436_0f98318b57d7ecec9a3c18f5be47437a7410596022594182 |
| CCA | CALCIUM ARSENATE | 砷酸钙 | 7778-44-1 | Cucumber dustTricalcium arsenateTricalcium ortho arsenate | pdf_6a8faacca882a39304796eef402a5436_e0bb566e151088403bb95d6b183dc1fd7410596022594182 |
| CCB | CALCIUM CARBIDE | 碳化钙（电石） |  | AcetylenogenCarbide | pdf_6a8faacca882a39304796eef402a5436_6e21aaaefac7f083504389460d291cd97410596022594182 |
| CCC | CALCIUM CHLORATE | 氯酸钙 | 10137-74-3 |  | pdf_6a8faacca882a39304796eef402a5436_39df124e6ed1fd131eec669f350cd9ea7410596022594182 |
| CCH | CYCLOHEXANONE | 环己酮 | 108-94-1 |  | pdf_6a8faacca882a39304796eef402a5436_925f91cf658de6d871e87ca063156a967410596022594182 |
| CCL | CYANOGEN CHLORIDE | 氯化氰 | 506-77-4 |  | pdf_6a8faacca882a39304796eef402a5436_efc2a9884d8ded9c3023f11621995f7b7410596022594182 |
| CCN | CALCIUM CYANIDE | 氰化钙 | 592-01-8 | Cyanide of calciumCyanogas A-dustCyanogas G-fumigant | pdf_6a8faacca882a39304796eef402a5436_a6574e1442186cff63343917273befc37410596022594182 |
| CCO | COBALT NITRATEcco | 硝酸钴 |  | Cobalt(II) nitrateCobaltous nitrateCobaltous nitrate hexahydrate | pdf_6a8faacca882a39304796eef402a5436_37ad46f14846bedfafd8dd0d4eb356087410596022594182 |
| CCP | CALCIUM PEROXIDE | 过氧化钙 | 1305-79-9 | Calcium dioxide | pdf_6a8faacca882a39304796eef402a5436_ee77d5b45cd120cb81f1609d3bb8a90f7410596022594182 |
| CCR | CALCIUM CHROMATE | 铬酸钙 | 13765-19-0 | Calcium chromate (vi)Calcium chromate dilydrateGebin yellow ultramarineSteinbuhi | pdf_6a8faacca882a39304796eef402a5436_44c223b885c796ee9b97863c76c110ea7410596022594182 |
| CCT | CREOSOTE, COAL TAR | 煤焦油杂酚油 |  |  | pdf_6a8faacca882a39304796eef402a5436_3a25ee76db60b2246363f96efd7959a57410596022594182 |
| CCY | COPPER CYANIDE (OUS) | 氰化亚铜 | 544-92-3 |  | pdf_6a8faacca882a39304796eef402a5436_840c876162701eda8c661ee9ebe23d967410596022594182 |
| CDA | CACODYLIC ACID | 二甲胂酸 | 75-60-5 |  | pdf_6a8faacca882a39304796eef402a5436_50c11e678b1b398b6eb3bf2608ee9b4d7410596022594182 |
| CDC | CADMIUM CHLORIDE | 氯化镉 | 10108-64-2 |  | pdf_6a8faacca882a39304796eef402a5436_b88819a5ff1348b5c97a2a8a9c8efce27410596022594182 |
| CDN | CHLORDANE | 氯丹 | 57-74-9 |  | pdf_6a8faacca882a39304796eef402a5436_b6ed00b2c97f82cb0883bdc076669d097410596022594182 |
| CDO | CARBON DIOXIDE | 二氧化碳 | 124-38-9 | Carbonic acid gasCarbonic anhydride | pdf_6a8faacca882a39304796eef402a5436_38c4ae8a56b5bceb89cbc68b770a66817410596022594182 |
| CES | CUPRIETHYLENEDIAMINE SOLUTION | 乙二胺铜溶液 | 13426-91-0 | Cupriethylenedamine hydroxidesolution | pdf_6a8faacca882a39304796eef402a5436_6f9c8c8f0866393e9933b8b23602dc717410596022594182 |
| CFB | CADMIUM FLUOROBORATE | 氟硼酸镉 | 14486-19-2 | Cadmium fluoroborateCadmium fluoroborate solution | pdf_6a8faacca882a39304796eef402a5436_ae7f0a2f1d238a35bad2468672aa85267410596022594182 |
| CFM | COBALT FORMATE | 甲酸钴 | 544-18-3 | Cobalt diformateCobaltous formate | pdf_6a8faacca882a39304796eef402a5436_1bb28ae9c82570fc7a254acf74bcf57a7410596022594182 |
| CGE | CRESYL GLYCIDYL ETHER | 甲苯基缩水甘油醚 | 26447-14-3 | Cresol, epoxypropyl etherTolyl epoxypropyl etherTolyl glycidyl ether | pdf_6a8faacca882a39304796eef402a5436_cd872d9d9a630de51eae107673fc16997410596022594182 |
| CHA | CYCLOHEXYLAMINE | 环己胺 | 108-91-8 | AninocyclohexaneHexahydroanine | pdf_6a8faacca882a39304796eef402a5436_08a8ecfb6e5eb22785b56c29dec209c47410596022594182 |
| CHC | CHARCOAL | 木炭 | 97793-37-8 | Activated charcoalAnimal carbonMineral carbonShell charcoalVegetable carbonWood  | pdf_6a8faacca882a39304796eef402a5436_d81b98b29416fddbb9ad35d8940872ed7410596022594182 |
| CHD | CHOROHYDRINS | 氯醇类 |  | Crude epichlorohydrin | pdf_6a8faacca882a39304796eef402a5436_b48520dc14695a296fece9523ded29cd7410596022594182 |
| CHM | CHOROACETIC ACID (80% OR LESS) | 氯乙酸（≤80%） | 79-11-8 |  | pdf_6a8faacca882a39304796eef402a5436_d26454697c90ea5bbcd1e5c4f0a0e8927410596022594182 |
| CHN | CYCLOHEXANOL | 环己醇 | 108-93-0 |  | pdf_6a8faacca882a39304796eef402a5436_fbfc88fa63be8108fa1979302e71f32d7410596022594182 |
| CHO | CHOROACETALDEHYDE | 氯乙醛 | 107-20-0 |  | pdf_6a8faacca882a39304796eef402a5436_37a27bcf72947f592a1a5e2cab764dee7410596022594182 |
| CHP | CYCLOHEXANONE PEROXIDE | 环己酮过氧化物 | 12262-58-7 |  | pdf_6a8faacca882a39304796eef402a5436_993504e83974fc69213968c6f8e883877410596022594182 |
| CHS | CHROMIC SULFATE | 硫酸铬 | 10101-53-8 |  | pdf_6a8faacca882a39304796eef402a5436_784ed539e706cd99b9949ec7bb1256787410596022594182 |
| CHT | CYCLOHEXENYLTRICHLOROSILANE | 环己烯基三氯硅烷 | 10137-69-6 |  | pdf_6a8faacca882a39304796eef402a5436_988d5143afe8d5cceb18105de56d233d7410596022594182 |
| CHX | CYCLOHEXANE | 环己烷 | 110-82-7 | HexahydrobenzeneHexamethyleneHexanaphthene | pdf_6a8faacca882a39304796eef402a5436_001f9ac601d0deee302689a5a25a9bca7410596022594182 |
| CHY | CALCIUM HPOCHLORITE | 次氯酸钙 | 7778-54-3 |  | pdf_6a8faacca882a39304796eef402a5436_2b5eeda5dea4f05b7de08b49874272897410596022594182 |
| CID | COPPER IODIDE | 碘化铜 | 13767-71-0 | Cuprous iodideMarshille | pdf_6a8faacca882a39304796eef402a5436_825e22519992419b75f123b3fd5a89447410596022594182 |
| CIT | CITRIC ACID | 柠檬酸 | 77-92-9 | 2-Hydroxy-1.2,3-propane-tricarboxylic acidbeta-Hydrox-tricarboxylic acidbeta-Hyd | pdf_6a8faacca882a39304796eef402a5436_860d519e9a0cb406d9fac8c809948eac7410596022594182 |
| CLA | 2-CHOROPROPIONIC ACID | 2-氯丙酸 | 598-78-7 | alpha-Chloroproponic acid Proponic acid, 2-chloro-Proponic acid, 2-chloro-Propon | pdf_6a8faacca882a39304796eef402a5436_d98f1345f2bfb5103c2f1280216474ec7410596022594182 |
| CLC | CALCIUM CHLORIDE | 氯化钙 | 10043-52-4 | Calcium chloride, anthyrousCalcium chloride hydratles | pdf_6a8faacca882a39304796eef402a5436_f1f41417b2064ed92043903f6ab221d17410596022594182 |
| CLD | COLLODION | 火棉胶 |  | Box toe gumBox lose nitrate solutionNitrocellulose gumNitrocellulose solutionPyr | pdf_6a8faacca882a39304796eef402a5436_86dc5bf22d32691378fa06aad12fe2407410596022594182 |
| CLP | 3-CHOROPROPIONIC ACID | 3-氯丙酸 | 107-94-8 |  | pdf_6a8faacca882a39304796eef402a5436_52ea37d194f6fa35cf65d39ed71250a77410596022594182 |
| CLS | CAPROLACTAM | 己内酰胺 | 105-60-2 | Aminocaproc lactamepison-CaprolactamHexahyydro-2h-azepine-2-one2-Koteoxamethyler | pdf_6a8faacca882a39304796eef402a5436_700bd2ce7989a30a671004150ffd940b7410596022594182 |
| CLT | COPPER LACTATE | 乳酸铜 | 16039-52-4 |  | pdf_6a8faacca882a39304796eef402a5436_79abed69ba85b817b6c55f140af400387410596022594182 |
| CLX | CHORINE | 氯 | 7782-50-5 |  | pdf_6a8faacca882a39304796eef402a5436_121ab0baf7a366a897bb501e16bef08d7410596022594182 |
| CMA | CHROMIC ANHYDRIDE | 三氧化铬（铬酸酐） | 1333-82-0 | Chromic acidChromic oxideChromium trioxide | pdf_6a8faacca882a39304796eef402a5436_0465cea8ba737e28aaf2fac53cc7baf87410596022594182 |
| CMB | CADMIUM BROMIDE | 溴化镉 | 7789-42-6 | Cadmium bromide tetrahydrate | pdf_6a8faacca882a39304796eef402a5436_b70b55a911c2fcbf3fa73af28da154097410596022594182 |
| CMC | CHROMYL CHLORIDE | 铬酰氯 | 14977-61-8 | Chromium (VI) dioxychlorideChromium oxychloride | pdf_6a8faacca882a39304796eef402a5436_49471c04e518ba195a4785148d5a689e7410596022594182 |
| CME | CHOROMETHYL METHYL ETHER | 氯甲基甲醚 | 107-30-2 | Methyl chloromethyl ether,arhydrousMonochloromethyl ether | pdf_6a8faacca882a39304796eef402a5436_bff51ca05dca74ee7e1d96cae17c15877410596022594182 |
| CMH | CUMENE HYDROPEROXIDE | 异丙苯过氧化氢 | 80-15-9 |  | pdf_6a8faacca882a39304796eef402a5436_66270612d32cf3eaabd9ca5ddc73ed527410596022594182 |
| CMN | CADMIUM NITRATE | 硝酸镉 | 10325-94-7 | Cadmium nitrate tetrahyrate | pdf_6a8faacca882a39304796eef402a5436_967f72216de3b0a0e00f5af145e8fabd7410596022594182 |
| CMO | CARBON MONOXIDEСМО | 一氧化碳 |  | Monoxide | pdf_6a8faacca882a39304796eef402a5436_e43fe7da400660f439f300cab35a50727410596022594182 |
| CMP | P-CYMENE | 对伞花烃 | 99-87-6 |  | pdf_6a8faacca882a39304796eef402a5436_8bcfe91affd3f95003c2d023eeeb2a217410596022594182 |
| CMS | CADMIUM SULFATE | 硫酸镉 | 10124-36-4 |  | pdf_6a8faacca882a39304796eef402a5436_9227f6e21b6eb4290b877361d190eba57410596022594182 |
| CNE | 1-CHLORO-1-NITROPROPANE | 1-氯-1-硝基丙烷 | 600-25-9 |  | pdf_6a8faacca882a39304796eef402a5436_6c2c7470bb5466546a5ba2802c5a7b9d7410596022594182 |
| CNI | COPPER NITRATE | 硝酸铜 | 3251-23-8 | Cupric nitrate trihydrateGerhardite | pdf_6a8faacca882a39304796eef402a5436_848b8fa0b5d8ae102b55ea17ae557def7410596022594182 |
| CNN | COPPER NAPHTHENATE | 环烷酸铜 |  | Paint drier | pdf_6a8faacca882a39304796eef402a5436_e204004ac4a0833e63656ef177bc99337410596022594182 |
| CNO | O-CHORONITROBENZENE | 邻氯硝基苯 | 88-73-3 | 1-Chloro-2-nitrobenzeneo-Nitrochlorobenzene | pdf_6a8faacca882a39304796eef402a5436_9bb8ee142b779cfca6a0676964e865bf7410596022594182 |
| CNT | CALCIUM NITRATE | 硝酸钙 | 10124-37-5 | Calcium nitrate tetrahydrate | pdf_6a8faacca882a39304796eef402a5436_f8ea764e848108fe6e11d4df456e0e467410596022594182 |
| COB | COBALT BROMIDE (OUS) | 溴化亚钴 | 7789-43-7 | Cobalt (ii) bromideCobalt dibromideCobaltous bromide | pdf_6a8faacca882a39304796eef402a5436_10ccf5d8bb4791700e4fa42f426a8c047410596022594182 |
| COF | COBALT FLUORIDE | 氟化钴 | 10026-17-2 | Cobalt difluorideCobalt (II) fluoride | pdf_6a8faacca882a39304796eef402a5436_7f4954ebbdc9ced1d3d297d40918fab17410596022594182 |
| COL | COPPER OXALATE | 草酸铜 | 814-91-5 | Cupric oxalite hemhydrate | pdf_6a8faacca882a39304796eef402a5436_3a45f3c77b609104a1f1eb79c77f64137410596022594182 |
| COP | COPPER ACETATE | 乙酸铜 |  |  | pdf_6a8faacca882a39304796eef402a5436_120924b7b47692fb4a671437d8992f067410596022594182 |
| COS | COBALT SULFAMATEcos | 氨基磺酸钴 |  | Cobalt amino sulfonateCobaltous sulfamateSulfatic acid, cobalt salt | pdf_6a8faacca882a39304796eef402a5436_4244a629302de44407f5305c252a2ddd7410596022594182 |
| COU | COUMAPHOScou | 蝇毒磷 |  |  | pdf_6a8faacca882a39304796eef402a5436_ef1210dfd175a4a87e13bd1640df90b17410596022594182 |
| COX | CADMIUM OXIDE | 氧化镉 | 1306-19-0 | Cadmium fume | pdf_6a8faacca882a39304796eef402a5436_9e177349c2990c89c71f302a99464adc7410596022594182 |
| CPA | COPPER ARSENITE | 亚砷酸铜 |  |  | pdf_6a8faacca882a39304796eef402a5436_c5e03f9b38bd3c3bb4ac70f0618a61907410596022594182 |
| CPB | COPPER BROMIDE | 溴化铜 |  | Cupric bromide, anhydrous | pdf_6a8faacca882a39304796eef402a5436_fb82b5b4ed5c6a3b24e596c38d27ddd37410596022594182 |
| CPC | COPPER CHLORIDE | 氯化铜 | 7447-39-4 | Cupric chloride dihydrateEriocolichite (anhydrous) | pdf_6a8faacca882a39304796eef402a5436_0515c93b49ddc7db7b731571e79d50017410596022594182 |
| CPE | CYCLOPENTENE | 环戊烯 | 142-29-0 | UN 2246 (DOT) | pdf_6a8faacca882a39304796eef402a5436_ecbf0fde0781ee939ed98f2563bc54517410596022594182 |
| CPF | COPPER FLUOROBORATE | 氟硼酸铜 | 207121-39-9 | Copper borofluoride solutionCopper(II) fluoborate solutionCupric fluoborate solu | pdf_6a8faacca882a39304796eef402a5436_83ddb4ccf41c00432d7dc236e17129a47410596022594182 |
| CPG | COPPER GLYCINATE | 甘氨酸铜 | 13479-54-4 |  | pdf_6a8faacca882a39304796eef402a5436_e898b6b13192f40ade54ef6ab2e1e8557410596022594182 |
| CPH | CAMPHENE | 莰烯 | 79-92-5 | 2.2-Dimethyl-3-methylenernotborane3.3-Dimethyl-2-methylenerorcamphane | pdf_6a8faacca882a39304796eef402a5436_07919aa0908dc21a6ef9ca2b5957566e7410596022594182 |
| CPL | CHOROPICRIN | 氯化苦 | 76-06-2 |  | pdf_6a8faacca882a39304796eef402a5436_3fe161f6927b119671dc649854902b137410596022594182 |
| CPN | P-CHOROPHENOL | 对氯苯酚 | 106-48-9 | 4-Chlorophenol | pdf_6a8faacca882a39304796eef402a5436_a2db45d0a9f0d19d3b08cb4562ee5c337410596022594182 |
| CPO | CAMPHOR OIL | 樟脑油 |  | Liquid camphorLiquid gum camphorLiquid impure camphor | pdf_6a8faacca882a39304796eef402a5436_d46b10116eb89a8e584d84ed89d6d64d7410596022594182 |
| CPP | CALCIUM PHOSPHIDE | 磷化钙 | 1305-99-3 | Photophor | pdf_6a8faacca882a39304796eef402a5436_1795b9f163a8e15837c5c11e3e3e829f7410596022594182 |
| CPR | CYCLOPROPANE | 环丙烷 | 75-19-4 | Trimethylene | pdf_6a8faacca882a39304796eef402a5436_655ee0198c9ffbee7e083115c78a338a7410596022594182 |
| CPS | CAUSTIC POTASH SOLUTION | 氢氧化钾溶液 | 1310-58-3 | LyePotassium hydroxide solution | pdf_6a8faacca882a39304796eef402a5436_f12d7f21e78faad3db9a91e74fa61e087410596022594182 |
| CPT | CAPTAN | 克菌丹 | 133-06-2 |  | pdf_6a8faacca882a39304796eef402a5436_cd5176eb09703f380b98f6cce9fb51de7410596022594182 |
| CRA | CHOROACETOPHENONE | 氯苯乙酮 | 532-27-4 | alpha-Chloracetophenoneomega-ChloracetophenoneChloromethyl phenyl ketonePhenacyl | pdf_6a8faacca882a39304796eef402a5436_3b8ad334d78ab357f1ac8d944feac7487410596022594182 |
| CRB | CHOROBENZENE | 氯苯 | 108-90-7 | Benzene chlorideMCBMonochlorobenzenePhenyl chloride | pdf_6a8faacca882a39304796eef402a5436_2f4378206ef1abd2851c40a6d41d99e07410596022594182 |
| CRC | CHROMOUS CHLORIDE | 氯化亚铬 | 10049-05-5 | Chromium chlorideChromium dichloride | pdf_6a8faacca882a39304796eef402a5436_4a57853f79d5b0a2322adb430aa8627b7410596022594182 |
| CRE | CALCIUM RESINATE | 树脂酸钙 |  |  | pdf_6a8faacca882a39304796eef402a5436_0bc4301f941488b5425afcbbee4c39537410596022594182 |
| CRF | CHOROFORM | 三氯甲烷（氯仿） | 67-66-3 | Trichloromethane | pdf_6a8faacca882a39304796eef402a5436_5c3f6acda45162ca038455344e139ac17410596022594182 |
| CRH | O-CHOROPHENOL | 邻氯苯酚 | 95-57-8 | 2-Chloro-1-Hydroxybenzane2-HydroxychlorobenzenePhenol,2-chloro-Phenol, o-chloro- | pdf_6a8faacca882a39304796eef402a5436_8be68eff657820e32ab53c43e1d9bc947410596022594182 |
| CRL | M-CRESOL | 间甲酚 | 108-39-4 |  | pdf_6a8faacca882a39304796eef402a5436_01bf34fa6bda2d0320c52a71907a64cb7410596022594182 |
| CRN | P-CHOROTOLUENE | 对氯甲苯 | 106-43-4 | 1-Chloro-4-methylbenzene4-Chloro-1-methylbenzene4-Chlorotoluenep-Tolyl chloride | pdf_6a8faacca882a39304796eef402a5436_49cbb4e854e1ffb4c7f3826b08d8abc57410596022594182 |
| CRO | O-CRESOL | 邻甲酚 | 95-48-7 |  | pdf_6a8faacca882a39304796eef402a5436_3fcfab619b5a27072ea2ffae30034e557410596022594182 |
| CRP | CHOROPRENE | 氯丁二烯 | 126-99-8 | 2-Chlorobutadine2-Chloro-1,3-butadiene2-Chlorobuta-1,3-dienebeta-Chloroprene | pdf_6a8faacca882a39304796eef402a5436_aa60cae952439a6a0a2b82236d4b20a27410596022594182 |
| CRS | CRESOLS | 甲酚（混合） |  |  | pdf_6a8faacca882a39304796eef402a5436_61374b3c25ede8d3662922a5f57cb4b57410596022594182 |
| CRT | CHROMIC ACETATE | 乙酸铬 | 1066-30-4 | Acetic acid, chromium saltChromic (III) acetateChromic acetateChromium triacetat | pdf_6a8faacca882a39304796eef402a5436_a30c3b7dc9a98ac6ebec15f30a01a7fb7410596022594182 |
| CSA | CHLOROSULFONIC ACID | 氯磺酸 | 7790-94-5 | Chlorosulfuric acidChlorosulfuric acidSulfuric chlorhydrin | pdf_6a8faacca882a39304796eef402a5436_7a124358615b5966cd4fa8994676d97f7410596022594182 |
| CSC | CRESYLATE SPENT CAUSTIC SOLUTION | 甲酚盐废碱液 |  | Cresylate spent caustic | pdf_6a8faacca882a39304796eef402a5436_06bf504a9f791e0c7bb868eba43a46de7410596022594182 |
| CSF | COPPER SULFATE | 硫酸铜 | 7758-98-7 | Blue vitrilCopper sulfate pentahydrateCupric sulfateSulfate of copper | pdf_6a8faacca882a39304796eef402a5436_268201dd5c30fd4626db2a050d58e2c17410596022594182 |
| CSN | COPPER SULFATE, AMMONIATED | 氨化硫酸铜 | 10380-29-7 | Ammonium cupric sulfateCopper ammonium sulfateCuprammonium sulfateCupric ammine  | pdf_6a8faacca882a39304796eef402a5436_3359b7dfe336b5b0164993d0252c415e7410596022594182 |
| CSO | P-CRESOLcso | 对甲酚 |  | 4-Hydroxytolusenep-Methylhydroxybenzenep-Methylphenylp-Toluol | pdf_6a8faacca882a39304796eef402a5436_1df1cc792085dac5e3747dff3eafddb87410596022594182 |
| CSS | CAUSTIC SODA SOLUTION | 氢氧化钠溶液 | 1310-73-2 |  | pdf_6a8faacca882a39304796eef402a5436_ff16c4be326b28b7ef7a6fee26ccb0767410596022594182 |
| CST | COPPER SUBACETATE | 碱式乙酸铜 |  | Basic copper acetateBlue verdigisCommon verdigisCupric acetate, basicFrench verd | pdf_6a8faacca882a39304796eef402a5436_a9ed7425f1be1376b0df834f2251958a7410596022594182 |
| CSY | CORN SYRUP | 玉米糖浆 |  |  | pdf_6a8faacca882a39304796eef402a5436_8ea6d4c7b23af47de1434466955e57f37410596022594182 |
| CTA | CROTONALDEHYDE | 巴豆醛 | 4170-30-3 |  | pdf_6a8faacca882a39304796eef402a5436_1642ec61962219762df69f6fb797a0ee7410596022594182 |
| CTC | CATECHOL | 邻苯二酚 | 120-80-9 | 1.2-BenzenedicolCatechin1.2-DihydroxybenzeneOxypheric acidPyrocatechinPyrocatech | pdf_6a8faacca882a39304796eef402a5436_b56ba4f9b8d5bf1196561df9e22e8b187410596022594182 |
| CTD | 4-CHLORO-O-TOLUIDINE | 4-氯邻甲苯胺 | 95-69-2 | 2-Amino-5-chlorotolune5-Chloro-2-amnotolune4-Chloro-2-methylanilineFast red TR b | pdf_6a8faacca882a39304796eef402a5436_5d796d1f70309a8eb098ad4024d9e3ac7410596022594182 |
| CTF | CHORINE TRIFLUORIDE | 三氟化氯 | 7790-91-2 |  | pdf_6a8faacca882a39304796eef402a5436_7fd23b8422076204075be64e1be571c87410596022594182 |
| CTM | M-CHOROTOLUENE | 间氯甲苯 | 108-41-8 | 1-Chloro-3-methylbenzene3-Chloro-1-methylbenzene3-Chlorotoluenem-Tolyl chloride | pdf_6a8faacca882a39304796eef402a5436_e0b36b281162eb363089fa5ef6e344e87410596022594182 |
| CTO | O-CHOROTOLUENE | 邻氯甲苯 | 95-49-8 | Benzene, 1-chloro2-methyl2-Chloro-1-methylbenzene2-Chlorotoluene1-Methyl2-chloro | pdf_6a8faacca882a39304796eef402a5436_6708b3cbb4ed95392ee30fd55800b2887410596022594182 |
| CTP | COAL TAR PITCH | 煤焦油沥青 |  |  | pdf_6a8faacca882a39304796eef402a5436_f8a9f6c077c633f2b5fe05e791bf7fae7410596022594182 |
| CTT | COPPER TARTRATE | 酒石酸铜 | 27004-40-6 | Tartaric acid, copper salt | pdf_6a8faacca882a39304796eef402a5436_e394d10f2735f102a704d903f501bf1c7410596022594182 |
| CUF | COPPER FORMATE | 甲酸铜 | 544-19-4 | Cupric diformateTubercuprose | pdf_6a8faacca882a39304796eef402a5436_856ed1ff127c42248ef1780c154710ca7410596022594182 |
| CUM | CUMENE | 异丙苯（枯烯） | 98-82-8 | CumloIsopropylbenzeneKeep people away.Call fire department.Avoid contact with li | pdf_6a8faacca882a39304796eef402a5436_380328239364c7233608817dd78de52b7410596022594182 |
| CWD | CREOSOTE (WOOD) | 木杂酚油 |  |  | pdf_6a8faacca882a39304796eef402a5436_73705aecb369c35e3cd835044a69e9367410596022594182 |
| CXY | CARBON OXYFLUORIDE | 碳酰氟 | 353-50-4 | Carbonic difluorideCarbonyl difluorideCarbonyl fluorideFluophosgeneFluoroformyl  | pdf_6a8faacca882a39304796eef402a5436_8a23b7207e829e2044f5dafa857bb2ee7410596022594182 |
| CYA | CYANOACETIC ACID | 氰基乙酸 | 372-09-8 | Cyanacetic acidMalonic mononitrile | pdf_6a8faacca882a39304796eef402a5436_3bb8fc9ab275974bd856046aeae4ec2f7410596022594182 |
| CYC | CYCLOHEXYL ACETATE | 乙酸环己酯 | 622-45-7 | Acetic acid, cyclohexyl esterCyclohexanyl acetateUN 2243 (DOT) | pdf_6a8faacca882a39304796eef402a5436_56f65f39d1ea6447b44688d6cdf008f77410596022594182 |
| CYE | CYCLOHEPTANE | 环庚烷 | 291-64-5 | UN 2241 (DOT) | pdf_6a8faacca882a39304796eef402a5436_95d862e184a312e68eea560c903b570d7410596022594182 |
| CYG | CYANOGEN | 氰 | 460-19-5 |  | pdf_6a8faacca882a39304796eef402a5436_2499f1ee4605f9a07fb874ba2c2e488d7410596022594182 |
| CYP | CYCLOPENTANE | 环戊烷 | 287-92-3 | Pentamethylene | pdf_6a8faacca882a39304796eef402a5436_ceb7faa61afe32056444925c623725c17410596022594182 |
| CYT | 1,5,9-CYCLODODECATRIENE | 1,5,9-环十二碳三烯 | 4904-61-4 |  | pdf_6a8faacca882a39304796eef402a5436_1414367dacb199d58b049043b6b8bd4f7410596022594182 |
| DAA | DIACETONE ALCOHOL | 双丙酮醇 | 123-42-2 | Diacetone4-Hydroxy-4-methyl-2-pentanoneTyranton | pdf_6a8faacca882a39304796eef402a5436_13a76a819e6c6b3b382a76f84e46f1887410596022594182 |
| DAC | DIMETHYLACETAMIDE | 二甲基乙酰胺 | 127-19-5 | Acetic acid, dimethylamideN-N-Dimethylacetamide | pdf_6a8faacca882a39304796eef402a5436_1495186af5274d5619f7261a773358aa7410596022594182 |
| DAE | N.N-DIETHYLETHANOLAMINE | N,N-二乙基乙醇胺 |  |  | pdf_6a8faacca882a39304796eef402a5436_543bc139fa0d76af4f8becf850cce17d7410596022594182 |
| DAI | DODECYLBENZENESULFONIC ACID, ISOPROPYLAMINE SALT | 十二烷基苯磺酸异丙胺盐 | 1135094-12-0 | Isopropylaminedodecylbenzenesulfonatedodecylbenzenesulfonatosedodium sodiumdodec | pdf_6a8faacca882a39304796eef402a5436_7fe1196eff0945c80987edba358ac1827410596022594182 |
| DAL | DECALDEHYDE | 癸醛 | 112-31-2 | Aldehyde C-10CapraldehydeCapric aldehydeDecarnaln-Decyl aldehyde | pdf_6a8faacca882a39304796eef402a5436_67a20b7e98c6d555d9547b765eb847f67410596022594182 |
| DAM | DIPHENYLAMINE | 二苯胺 | 122-39-4 | AnilinobenzeneN-Phenylanine | pdf_6a8faacca882a39304796eef402a5436_61dc3395abc3cfe186bc013becf0915d7410596022594182 |
| DAN | N-DECYL ALCOHOL | 正癸醇 | 112-30-1 |  | pdf_6a8faacca882a39304796eef402a5436_74e5875fa8897cf33683d13517923bf07410596022594182 |
| DAP | DI-N-AMYL PHTHALATE | 邻苯二甲酸二戊酯 | 131-18-0 | Diamyl phthalateDipenty phthalatePhthalic acid, diamyl esterPhthalic acid, dipen | pdf_6a8faacca882a39304796eef402a5436_c44598ff860c04337cf95f13925b685e7410596022594182 |
| DAR | N-DECYL ACRYLATE | 丙烯酸癸酯 | 2156-96-9 |  | pdf_6a8faacca882a39304796eef402a5436_efcf1b37f633ab46433dfdb0f99f7b3f7410596022594182 |
| DAS | DODECYL BENZENE SULFONIC ACID. SODIUM SALT | 十二烷基苯磺酸钠 |  |  | pdf_6a8faacca882a39304796eef402a5436_134032175c40d6feb949a97da20b80947410596022594182 |
| DBA | DI-N-BUTYLAMINE | 二正丁胺 | 111-92-2 | 1-Butanamine, n-butylDibutylamine | pdf_6a8faacca882a39304796eef402a5436_8924a38652087b9fe82678991726d6897410596022594182 |
| DBC | DIISOBUTYLCARBINOL | 二异丁基甲醇 | 108-82-7 | 2.8-Dimethyl-4-heptanol | pdf_6a8faacca882a39304796eef402a5436_bd23e1d2acd28bb2265239948f5aaa097410596022594182 |
| DBE | DI-N-BUTYL ETHER | 二正丁醚 | 142-96-1 | 1-Butoxy butaneBulyl ethern-Bulyl etherDibuty ethern-Dibuty etherDibuty oxide | pdf_6a8faacca882a39304796eef402a5436_8ed4b7c5b02c6bae77fad27df977582c7410596022594182 |
| DBH | DIBROMOMETHANE | 二溴甲烷 | 74-95-3 |  | pdf_6a8faacca882a39304796eef402a5436_0a5f18be6a7c9c4d226604242052948a7410596022594182 |
| DBK | DI-N-BUTYL KETONE | 二正丁基酮 | 502-56-7 | 5-Nonanone5-Noranone | pdf_6a8faacca882a39304796eef402a5436_17f5eb1bc825ffdea353c3c1f8c087fc7410596022594182 |
| DBL | DIISOBUTYLENE | 二异丁烯 | 107-39-1 | 2,4,4-Trimethyl-1-pentene | pdf_6a8faacca882a39304796eef402a5436_195aff8ae5d3192d72cd4f8bc21787877410596022594182 |
| DBM | M-DICHOROBENZENE | 间二氯苯 | 541-73-1 | 1.3-Dichlorobenzemeta-Dichlorobenzemeta-Dichlorobenzemeta-Dichlorobenzemeta-Dich | pdf_6a8faacca882a39304796eef402a5436_c11a3d8770ab6cd3fcc9d4270061ee6d7410596022594182 |
| DBN | DIBENZYL ETHER | 二苄醚 | 103-50-4 |  | pdf_6a8faacca882a39304796eef402a5436_555b0fa39f0f244cce48258b9d7000ab7410596022594182 |
| DBO | O-DICHOROBENZENE | 邻二氯苯 | 95-50-1 | 1.2-Dichlorobenzeneortho-DichlorobenzeneDowtherme | pdf_6a8faacca882a39304796eef402a5436_ba0040a9bc0822a069f068704023e74d7410596022594182 |
| DBP | P-DICHOROBENZENE | 对二氯苯 | 106-46-7 |  | pdf_6a8faacca882a39304796eef402a5436_1a1aa78456c6e050c29341a26799a8297410596022594182 |
| DBR | DECABORANE | 癸硼烷 |  |  | pdf_6a8faacca882a39304796eef402a5436_6fe3bc94929293de328086f464472f3d7410596022594182 |
| DBS | DODECYLBENZENESULFONIC ACID, TRIETHANOLAMINE SALT | 十二烷基苯磺酸三乙醇胺盐 | 27323-41-7 | Triethanolaminedodeceylbenzenesulfonate | pdf_6a8faacca882a39304796eef402a5436_3fb8a77f4a9b49c948eabdac43c7a0647410596022594182 |
| DBT | DIBUTYLPHENOL | 二丁基苯酚 | 26967-68-0 | 2.6-DI-tert-butylphenol | pdf_6a8faacca882a39304796eef402a5436_8a3442bdc070934c6a762212eec43c377410596022594182 |
| DBU | DIISOBUTYLAMINE | 二异丁胺 | 110-96-3 |  | pdf_6a8faacca882a39304796eef402a5436_64a38654db6c03bb7a918e60800fea177410596022594182 |
| DBZ | N-DECYLBENZENE | 癸基苯 | 104-72-3 | Decy/benzene1-Phenyldecane | pdf_6a8faacca882a39304796eef402a5436_f341a227c2569b6a97d7bf4a04f3810e7410596022594182 |
| DCA | 2,4-DICHOROPHENOXYACETIC ACID | 2,4-二氯苯氧乙酸（2,4-D） | 94-75-7 | 2.4-D | pdf_6a8faacca882a39304796eef402a5436_c04ace2737eb1930af254e1f7ff6af177410596022594182 |
| DCB | DICHOROBUTENE | 二氯丁烯 | 11069-19-5 |  | pdf_6a8faacca882a39304796eef402a5436_908d60596544a852ad6bab76c851ea0b7410596022594182 |
| DCC | DECANE | 癸烷 | 124-18-5 | n-Decane | pdf_6a8faacca882a39304796eef402a5436_14c71161c0a1326c1fa25a7211015feb7410596022594182 |
| DCE | 1-DECENE | 1-癸烯 | 872-05-9 | alpha-Decene | pdf_6a8faacca882a39304796eef402a5436_bef58599384b566b8f2ef13dc947d0117410596022594182 |
| DCF | DICHORODIFLUOROMETHANE | 二氯二氟甲烷 | 75-71-8 |  | pdf_6a8faacca882a39304796eef402a5436_95efed243dfe9e5fc24a5888a11c878f7410596022594182 |
| DCH | 1,1-DICHOROETHANE | 1,1-二氯乙烷 | 75-34-3 | Chlorinated hydrochloric etherEthylidene chlorideEthylidene dichloride | pdf_6a8faacca882a39304796eef402a5436_89f165e5e66e4363a712086181d064b47410596022594182 |
| DCI | 2,2'-DICHOROISOPRYL ETHER | 2,2'-二氯异丙醚 |  | Bis (2-Chlorisopropyl) etherEther, bis(2-chloro-1-methylethyl) | pdf_6a8faacca882a39304796eef402a5436_35220cf8756b781f2096dc5d0bf954577410596022594182 |
| DCL | DICHLONE | 二氯萘醌 | 117-80-6 | 2.3-Dichioro-1.4-naphthoquinonePhygonPhygon-XL | pdf_6a8faacca882a39304796eef402a5436_fb2e011c94482fe6fd135a83d821c35e7410596022594182 |
| DCM | DICHOROMETHANE | 二氯甲烷 | 75-09-2 | Methylene chlorideMethylene dichloride | pdf_6a8faacca882a39304796eef402a5436_6ee71ef0bddec58aea47221e6237bcc77410596022594182 |
| DCO | DECANOIC ACID | 癸酸 | 334-48-5 |  | pdf_6a8faacca882a39304796eef402a5436_a7794c3cd66f68cb76db88cd4408f4917410596022594182 |
| DCP | 2.4-DICHOROPHENOL | 2,4-二氯苯酚 |  |  | pdf_6a8faacca882a39304796eef402a5436_2b2473ef5b7884a0160f63aead33317e7410596022594182 |
| DCR | N,N-DIMETHYLCARBAMOYL CHLORIDE | N,N-二甲基氨基甲酰氯 | 79-44-7 |  | pdf_6a8faacca882a39304796eef402a5436_59f4e1ca96bf4b50f12cf5cb661dddf77410596022594182 |
| DCS | DODECYLBENZENESULFONIC ACID, CALCIUM SALT | 十二烷基苯磺酸钙 | 26264-06-2 | Calcium alkylomatic sulfonateCalcium alkylbenzenesulfonate | pdf_6a8faacca882a39304796eef402a5436_7d392dd2fae3949a443491a15cead5407410596022594182 |
| DCT | 1,1-DICHORO-1-NITROETHANE | 1,1-二氯-1-硝基乙烷 | 594-72-9 |  | pdf_6a8faacca882a39304796eef402a5436_6b1068034f87b7780a41f826dc140ea97410596022594182 |
| DCV | DICHLORVOS | 敌敌畏 | 62-73-7 |  | pdf_6a8faacca882a39304796eef402a5436_0a1de04b5f2d0460f4fe88bef7e9d0b47410596022594182 |
| DCY | 4,6-DINITRO-O-CYCLOHEXYL PHENOL | 4,6-二硝基邻环己基苯酚 |  | 2-Cyclohexyl-4,6-dinitrophenol2,4-Dinitro-6-cyclohexylphenolDinitro-o-cyclohexyl | pdf_6a8faacca882a39304796eef402a5436_33d228787caea064380f20273b16eeba7410596022594182 |
| DDB | DODECYLBENZENE | 十二烷基苯 | 123-01-3 | Detergent alkylaten-DodecylenzeneLaurybenzene1-PhenyldodecaneUcane alkylate 12 | pdf_6a8faacca882a39304796eef402a5436_3830ed14d3dfa96e69d24dec7b2368d27410596022594182 |
| DDC | 1-DODECENE | 1-十二烯 | 112-41-4 | Adacene-12 alpha-Dodecylene | pdf_6a8faacca882a39304796eef402a5436_1c3f1420a92d5611844689bb727cddf97410596022594182 |
| DDD | DDD | 滴滴滴（DDD） | 72-54-8 | 1,1-Dichloro-2-2-bis(p-chlorophenyl) ethaneDichlorodiphenyldichloroethaneTDE | pdf_6a8faacca882a39304796eef402a5436_cb9f3c8fa5f3b5625f0cb3ad51a26b047410596022594182 |
| DDI | 2,2-DIMETHYLPROPANE-1,3-DIOL | 新戊二醇 | 126-30-7 | Dimethyl propanedimethyl/trimethylene glycolNeolNeopentylene glycolNeopentylene  | pdf_6a8faacca882a39304796eef402a5436_464675dd3b67cb11d01e034e621f9d827410596022594182 |
| DDM | DODECYLMETHACRYLATE | 甲基丙烯酸十二酯 |  | Dodecycl-2-methyl-2-propenoateLauryl methacrylateMethacrylic acid, dodecyl ester | pdf_6a8faacca882a39304796eef402a5436_70fd8b152ecb3cadfb240ea7095a46327410596022594182 |
| DDN | DODECANOL | 十二醇 | 112-53-8 | Dodecyl alcoholLaury alcohol | pdf_6a8faacca882a39304796eef402a5436_23bb0c61acb75e10531deb4a111ace2a7410596022594182 |
| DDP | DODECYL/PENTADECYL METHACRYLATE | 甲基丙烯酸十二/十五酯 |  | Methacrylic acid, dodecyl and pentadecyster mxiMethacrylic acid, lauryl and pent | pdf_6a8faacca882a39304796eef402a5436_b51a5e631327c4faa04e408984553da07410596022594182 |
| DDS | DODECYL SULFATE, SODIUM SALT | 十二烷基硫酸钠 | 151-21-3 |  | pdf_6a8faacca882a39304796eef402a5436_1d3ee15d790659fcbca8a2416275703e7410596022594182 |
| DDT | DDT | 滴滴涕（DDT） | 50-29-3 | p.g.-DDT Dichlorodiphenyltrichloroethane 1,1,1-Trichloro-2,2-bis(p-chlorophenyl) | pdf_6a8faacca882a39304796eef402a5436_40d29977fcc59fee1fac7e10254d84eb7410596022594182 |
| DDW | DIMETHYLHEXANE DIHYDROPEROXIDE | 二甲基己烷二氢过氧化物 |  | 2.5-Dihydroperoxy-2.5-dimethylhexane2.5-Dimethylhexane-2.5-dihydroperoxide | pdf_6a8faacca882a39304796eef402a5436_5d4081cda3e097c7eeaab9e39c9710d07410596022594182 |
| DEA | DIETHANOLAMINE | 二乙醇胺 | 111-42-2 |  | pdf_6a8faacca882a39304796eef402a5436_384d2e8020c56e8db95a3756823388b77410596022594182 |
| DEB | DIETHYLBENZENE | 二乙苯 |  |  | pdf_6a8faacca882a39304796eef402a5436_cbe74f4868982b88ef7c6eb667e7de997410596022594182 |
| DEC | DIETHYL CARBONATE | 碳酸二乙酯 | 105-58-8 | Carbonic acid, diethyl esterEthyl carbonateEufin | pdf_6a8faacca882a39304796eef402a5436_b067bff529b28d070ef833fc44fd0ff07410596022594182 |
| DED | DIELDRIN | 狄氏剂 | 60-57-1 |  | pdf_6a8faacca882a39304796eef402a5436_075d3c07dffda6788159471cae78d45d7410596022594182 |
| DEE | 2.2-DICHOROETHYL ETHER | 2,2-二氯乙醚 |  |  | pdf_6a8faacca882a39304796eef402a5436_d3709f362584281bc0d03022879b2e5e7410596022594182 |
| DEG | DIETHYLENE GLYCOL | 二甘醇 | 111-46-6 | DEGDiglycolBis-(2-Hydroxyethyl)ether3-Ox-1, 5-pertanediodi2,2&#x27 -Oxylisethano | pdf_6a8faacca882a39304796eef402a5436_438dfbeff218cd7de5272663dc2a431e7410596022594182 |
| DEH | DI-(2-ETHYLHEXYL) ADIP | 己二酸二（2-乙基己基）酯 |  | Adipic, bis (2-ethyhexyy)lesterBis(2-ethyhexyy) adipate | pdf_6a8faacca882a39304796eef402a5436_7fc48ed00c090e3dcf1efa5614cc19de7410596022594182 |
| DEK | DIETHYL KETONE | 二乙基酮 | 96-22-0 |  | pdf_6a8faacca882a39304796eef402a5436_d57fb0bbf043ef041aa5f9e66e44c0b07410596022594182 |
| DEL | 1,2-DICHOROETHYLENE | 1,2-二氯乙烯 | 540-59-0 | Acetylene dichloridetrans-1,2-Dichloroethylenesis-1,2-Dichloroethylenesym-Dichlo | pdf_6a8faacca882a39304796eef402a5436_822bacaaeca8cd2b6b649619b02190827410596022594182 |
| DEM | DIETHYLENE GLYCOL MONOBUTYL ETHER ACETATE | 二甘醇单丁醚乙酸酯 | 124-17-4 | 2-(2-Butoxyethoxy) ethanolacetateBully&#x27 carbitol&quot acetateDiglycol monobu | pdf_6a8faacca882a39304796eef402a5436_0a896aed19b7aa7a62fc3cf68c43c6ba7410596022594182 |
| DEN | DIETHYLAMINE | 二乙胺 | 109-89-7 | DEN | pdf_6a8faacca882a39304796eef402a5436_4432c046ba06338971845a71662bb3677410596022594182 |
| DEP | DI-(2-ETHYLHEXYL)PHOSPHORIC ACID | 二（2-乙基己基）磷酸 | 298-07-7 |  | pdf_6a8faacca882a39304796eef402a5436_833e68742dc07472ed637fa01c585f3a7410596022594182 |
| DER | BUTYL, DECYL, CETYL-EICOSYL METHACRYLATE | 丁基/癸基/十六烷基-二十烷基甲基丙烯酸酯 |  | Butyl, decyl, cetyl, eicosyl 2-methacrylic acid, butyl, decyl,cetyl and eicosyl  | pdf_6a8faacca882a39304796eef402a5436_100fd3076ce9018ec8d0c753d3f700e37410596022594182 |
| DES | 2,4-D ESTERS | 2,4-D酯类 |  | Butyl 2,4-dichlorophenoxycateate 2,4-Dichlorophenoxycateic acid, butoxyethyl est | pdf_6a8faacca882a39304796eef402a5436_dec55153faf093b30bf6263c17157f557410596022594182 |
| DET | DIETHYLENETRIAMINE | 二乙烯三胺 | 111-40-0 | Bis-(2-Aminoethyl) anime2,2&#x27 -Diaminodethylamine | pdf_6a8faacca882a39304796eef402a5436_fa4372567442e57cae6fdb4fd08a40187410596022594182 |
| DEZ | DIETHYLINC | 二乙基锌 |  | EthylzincZinc diethylZinc ethyl | pdf_6a8faacca882a39304796eef402a5436_41052403e220156c263a35d10c4032647410596022594182 |
| DFA | DIFLUOROPHOSPHORIC A | 二氟磷酸 |  | Difluorophosphorous acid | pdf_6a8faacca882a39304796eef402a5436_17764b8fc96ef58309b256cd66e951177410596022594182 |
| DFE | 1,1-DIFLUOROETHANE | 1,1-二氟乙烷 | 75-37-6 | Ethylidene fluorideEthylidene fluorideRefrigerant 152A | pdf_6a8faacca882a39304796eef402a5436_b7d5dae23be96a9307d0d13a7f9177527410596022594182 |
| DFF | DISTILLATES: FLASHED FEED STOCKS | 馏分油（闪蒸进料） |  | Petroleum distillate | pdf_6a8faacca882a39304796eef402a5436_56982c26f331043944749a9bddc2deb27410596022594182 |
| DFM | DICHOROMONOFLUOROMETHANE | 二氯一氟甲烷 | 75-43-4 | DichlorofluoromethaneF-21FluorodichloromethaneFreon 21Halocarbon 21Halon 112R-21 | pdf_6a8faacca882a39304796eef402a5436_9bf1a53b926c3d1ae0e9e7ccd32006767410596022594182 |
| DGA | DIETHYLENE GLYCOL ETHYL ETHER ACETATE | 二甘醇乙醚乙酸酯 | 112-15-2 |  | pdf_6a8faacca882a39304796eef402a5436_98c9d3ee32812495693c93c4d4a1ba067410596022594182 |
| DGD | DIETHYLENE GLYCOL DIMETHYL ETHER | 二甘醇二甲醚 | 111-96-6 | DiglymeBis-(2-Methoxyethyl)-etherPoly solv | pdf_6a8faacca882a39304796eef402a5436_969c8155fc8e6d21c4745864d26833957410596022594182 |
| DGE | DIETHYLENE GLYCOL MONOBUTYL ETHER | 二甘醇单丁醚 | 112-34-5 | Butoxydethylene glycolButoxydiglycol2-4-2-Butoxyethoxy) ethanolButyl &quot carbi | pdf_6a8faacca882a39304796eef402a5436_f4b87b8271ab8ae7a2a45a81863656fa7410596022594182 |
| DGL | DIETHYLENE GLYCOL PHTHALATE | 二甘醇邻苯二甲酸酯 | 7447-67-8 |  | pdf_6a8faacca882a39304796eef402a5436_42da93305ff6c90ed2c3a2c91b251d547410596022594182 |
| DGM | DIETHYLENE GLYCOL MONOMETHYL ETHER | 二甘醇单甲醚 | 111-77-3 | Diethylene glycol methyl etherDowanol DM2-(2-Methoxythoxy)-ethanolMethyl carbito | pdf_6a8faacca882a39304796eef402a5436_73b2c8dc0f4267f83222d93d24e65c467410596022594182 |
| DGR | DIETHYLENE GLYCOL METHYL ETHER ACETATE | 二甘醇甲醚乙酸酯 | 110-49-6 | Methyl carbitol acetate | pdf_6a8faacca882a39304796eef402a5436_c560fb79e6a60a2abb03c6a544c302087410596022594182 |
| DGT | DIMETHYL GLUTARATE | 戊二酸二甲酯 | 1119-40-0 |  | pdf_6a8faacca882a39304796eef402a5436_7d19db2d87ffcbd885253b0716fcb70d7410596022594182 |
| DGY | DIPROPYLENE GLYCOL DIBENZOATE | 二丙二醇二苯甲酸酯 |  | Benzoflex 9-88 Benzoflex 9-88 SG Benzoflex 9-88 Dibenzol dipropylene glycol este | pdf_6a8faacca882a39304796eef402a5436_f6d4cc22e902fbb4003caf200c0f193a7410596022594182 |
| DHA | DI-N-HEXYL ADIP | 己二酸二正己酯 |  |  | pdf_6a8faacca882a39304796eef402a5436_a6d35140a05245a0c953c1d9d5e226f07410596022594182 |
| DHE | DIETHYLENE GLYCOL N-HEXYL ETHER | 二甘醇正己醚 | 112-59-4 | Hexyl carbitol | pdf_6a8faacca882a39304796eef402a5436_776402fb16bed14725ba56770fbcc5597410596022594182 |
| DHN | DECAHYDRONAPHTHALENE | 十氢化萘 | 91-17-8 | Bicyclo[4.4.0]DecaneDECDecalinDE KalinNaphthalanePerthyronapthalene | pdf_6a8faacca882a39304796eef402a5436_8b2e26231cdc07f9e7d43b17e88221db7410596022594182 |
| DHP | DIHEPTYL PHTHALATE | 邻苯二甲酸二庚酯 | 3648-21-3 | Phthalic acid, diheptyl ester | pdf_6a8faacca882a39304796eef402a5436_e7724f4520eb9656a05fc1b3df8824c67410596022594182 |
| DHX | 1,6-DICHOROHEXANE | 1,6-二氯己烷 | 2163-00-0 |  | pdf_6a8faacca882a39304796eef402a5436_7b412e9ea1e8de85c3fb09f61700adeb7410596022594182 |
| DIA | DIISOPROPYLAMINE | 二异丙胺 | 108-18-9 |  | pdf_6a8faacca882a39304796eef402a5436_1184aed794638efc0ac1d92091f950e87410596022594182 |
| DIB | DICHLOBENIL | 敌草腈 | 1194-65-6 |  | pdf_6a8faacca882a39304796eef402a5436_af7310c5270af6960e26a2b03a4ea43f7410596022594182 |
| DIC | DICAMBA | 麦草畏 | 1918-00-9 |  | pdf_6a8faacca882a39304796eef402a5436_97ef239dd5172ea72a7f3fab1c1aadc27410596022594182 |
| DID | DIISODECYL PHTHALATE | 邻苯二甲酸二异癸酯 | 26761-40-0 | Pithalic acid, disodecyl esterPthalic acid, bis (8-methyl-nonyl) esterPlasticize | pdf_6a8faacca882a39304796eef402a5436_2ed579986e49353b21aa5797731a77647410596022594182 |
| DIE | DI-(2-ETHYLHEXYL) PHTHALATE | 邻苯二甲酸二（2-乙基己基）酯（DOP） | 117-81-7 |  | pdf_6a8faacca882a39304796eef402a5436_36516f98929e6e48b868ec81e540ce537410596022594182 |
| DIF | DINONYL PHTHALATE | 邻苯二甲酸二壬酯 | 84-76-4 |  | pdf_6a8faacca882a39304796eef402a5436_723d07ecae30700eb9d8835f1ab469b17410596022594182 |
| DIG | DIETHYLENE GLYCOL DIBUTYL ETHER | 二甘醇二丁醚 | 112-73-2 | Bis(2-Butoxyethyl) etherButyl digiyme2.2&#x27 -Dibutoxyethyl etherDibutyl carbit | pdf_6a8faacca882a39304796eef402a5436_071bdf02279074b0b28f50ee3438a4a07410596022594182 |
| DIH | DIISOPROPYLBENZENE HYDROPEROXIDE | 二异丙苯过氧化氢 |  | Isopropylcumyl hydroperoxide | pdf_6a8faacca882a39304796eef402a5436_e6aac335d8c22ac525b77a8ce1fffe267410596022594182 |
| DII | DIISOPROPYL NAPHTHALENE | 二异丙基萘 | 94133-79-6 | 2.6-Disopropyl naphthalene | pdf_6a8faacca882a39304796eef402a5436_6be51319218bf06d24c124ad452aa2837410596022594182 |
| DIK | DIISOBUTYL KETONE | 二异丁基酮 | 108-83-8 |  | pdf_6a8faacca882a39304796eef402a5436_51ad4c60e00ce1118e65d81e33f4c68e7410596022594182 |
| DIL | DIPHENYL | 联苯 | 92-52-4 |  | pdf_6a8faacca882a39304796eef402a5436_ff3a33b2ce50e535a8788bce7b304bd87410596022594182 |
| DIM | DIMETHYL ETHER | 二甲醚 | 115-10-6 | Methyl etherWood ether | pdf_6a8faacca882a39304796eef402a5436_e61c78eb6b03f0b499faf9cfa6ee80797410596022594182 |
| DIN | DIISONONYL PHTHALATE | 邻苯二甲酸二异壬酯 | 28553-12-0 | 1.2-Benzenedicarboxylic acid,di-isonyl esterDi(7-methylocty) phthalatePhthalic a | pdf_6a8faacca882a39304796eef402a5436_1662a26608d8dc135bd5e1b89b538b227410596022594182 |
| DIO | DIISOOCTYL PHTHALATE | 邻苯二甲酸二异辛酯 | 27554-26-3 |  | pdf_6a8faacca882a39304796eef402a5436_fae0270a710bd2275404e9694ff117217410596022594182 |
| DIP | DIISOPROPANOLAMINE | 二异丙醇胺 | 110-97-4 | 2.2&#x27 -Dihydrox-dipropylamine1.1-Inminodi-2-propanol | pdf_6a8faacca882a39304796eef402a5436_ed5c1d775eeba4bb717c156dd156d2907410596022594182 |
| DIQ | DIQUAT | 敌草快 | 2764-72-9 |  | pdf_6a8faacca882a39304796eef402a5436_f7506873820f5900fba7696d1cddbaad7410596022594182 |
| DIS | DISULFOTON | 乙拌磷 | 298-04-4 | O.O-Diethyl-5-2-(ethylthio)ethylphosphodithioateDi-systonDithiosystoxThiodemeton | pdf_6a8faacca882a39304796eef402a5436_62465aaad3e1914e6b080680454ee97d7410596022594182 |
| DIT | DIISOBUTYL PHTHALATE | 邻苯二甲酸二异丁酯 | 84-69-5 | 1.2-Benzene dicarboxylic acid, di-(2-methyl/propyl)sterHexaplas M1BIsobulyl phth | pdf_6a8faacca882a39304796eef402a5436_0a5ba6f8f863ef7e6ffc4dd5bff6e4d17410596022594182 |
| DIU | DIURON | 敌草隆 | 330-54-1 | DichlorfendismDi-onDiurexKarmexMarmer | pdf_6a8faacca882a39304796eef402a5436_f9d32e106b32a687b39ed69eef5e416f7410596022594182 |
| DIX | DIISOPROPYLBENZENE (ALL ISOMERS) | 二异丙苯（各异构体） | 25321-09-9 | Benzene, disopropyl Cumune buttons DIPB bis-(1-Methylethyl)-benzene | pdf_6a8faacca882a39304796eef402a5436_e3cd1278a6ceaef074c3ac0bf1c3d2347410596022594182 |
| DLA | DIMETHYL ADIPATE | 己二酸二甲酯 | 627-93-0 | Adipic acid, dimethyl esterDimethyl hexanodiateHexanedioic acid, dimethylesterMe | pdf_6a8faacca882a39304796eef402a5436_3ff6931724239a4be536755a11cc3e847410596022594182 |
| DLP | 2,2-DICHOROPROPANOIC ACID | 2,2-二氯丙酸 | 75-99-0 |  | pdf_6a8faacca882a39304796eef402a5436_4d611fd015c6b7bce94936f266ef41307410596022594182 |
| DLS | N,N-DIMETHYL ACETAMIDE SOLUTION (40% OR LESS) | N,N-二甲基乙酰胺溶液（≤40%） | 127-19-5 | Acetic acid, dimethylamideDimethylacetamide | pdf_6a8faacca882a39304796eef402a5436_2a412c46ccbfe80c3d96bdc46cc0fd937410596022594182 |
| DMA | DIMETHYLAMINE | 二甲胺 | 124-40-3 |  | pdf_6a8faacca882a39304796eef402a5436_a18f8c093227664acdb475179b7530d37410596022594182 |
| DMB | DIMETHYLETHANOLAMINE | 二甲基乙醇胺 | 108-01-0 |  | pdf_6a8faacca882a39304796eef402a5436_85b4b7b2c3438109f6c2dc767c3c76827410596022594182 |
| DMD | DIMETHYLDICHLOROSILANE | 二甲基二氯硅烷 | 75-78-5 |  | pdf_6a8faacca882a39304796eef402a5436_e2de911fc6a931715d266af9ab7b28aa7410596022594182 |
| DME | DIETHYLENE GLYCOL MONOBUTYL ETHER | 二甘醇单丁醚 | 112-34-5 | Butoxydethylene glycolButoxydiglycol2-4-2-Butoxyethoxy) ethanolButyl &quot carbi | pdf_6a8faacca882a39304796eef402a5436_b1c384db2e8ccbc24610784db71782a07410596022594182 |
| DMF | DIMETHYLFORMAMIDE | 二甲基甲酰胺（DMF） | 68-12-2 | N.N-DimethyformamideDMF | pdf_6a8faacca882a39304796eef402a5436_b953f03fc75f76652e3f7cdc19a3f6767410596022594182 |
| DMH | 1,1-DIMETHYLHYDRAZINE | 1,1-二甲基肼（偏二甲肼） | 57-14-7 | Dimazineunsym-DimethylhydrazineUDMH | pdf_6a8faacca882a39304796eef402a5436_d787362fee84890c5345f014b2a9fcdb7410596022594182 |
| DML | 1,2-DIMETHYLHYDRAZINE | 1,2-二甲基肼 | 540-73-8 | sym-DimethylthydrazinesDMH | pdf_6a8faacca882a39304796eef402a5436_f2b5dcce40a6216c1466c77455fbac297410596022594182 |
| DMM | 2,6-DIMETHYLANILINE | 2,6-二甲基苯胺 | 87-62-7 |  | pdf_6a8faacca882a39304796eef402a5436_3e5d02d41333e91c17faf189cdd2ce3b7410596022594182 |
| DMN | 2.6-DIETHYLANILINE | 2,6-二乙基苯胺 | 579-66-8 | Aniline, 2,6-diethylBenzeneamine, 2,6-diethyl-(9c) | pdf_6a8faacca882a39304796eef402a5436_96fd5ff4ee110e70053234d4f861258b7410596022594182 |
| DMO | 2.2-DIMETHYLOCTANOIC ACID | 2,2-二甲基辛酸 |  | 2.2-Dimethylcaryplic acid | pdf_6a8faacca882a39304796eef402a5436_d562d062937221fe7e5ea9ca7d2760817410596022594182 |
| DMP | DIMETHYLPOLYSILOXANE | 聚二甲基硅氧烷 |  | Dimethyl silicone fluidsPoly(dimethylsiloxane)Silicone fluids | pdf_6a8faacca882a39304796eef402a5436_e6197ae0a656aa0f9d950ae7035e6c677410596022594182 |
| DMS | DIMETHYL SULFOXIDE | 二甲基亚砜（DMSO） | 67-68-5 | DMSOMethyl sulfoxide | pdf_6a8faacca882a39304796eef402a5436_b0282e29351a66415b6d51e452430ddf7410596022594182 |
| DMT | DIMETHYL TEREPHTHALATE | 对苯二甲酸二甲酯 | 120-61-6 | Terephthalic acid, dimethyl ester | pdf_6a8faacca882a39304796eef402a5436_d3b2ff66359bf89268fd552619161f4b7410596022594182 |
| DMX | DICHLOROPROPENE, DICHLOROPROPANE MIXTURE | 二氯丙烯/二氯丙烷混合物 |  | D-D soil fumigant1,3-Dichloropropene and 1,2-DichloropropaneDowfume NTeloneVidde | pdf_6a8faacca882a39304796eef402a5436_e90780d10cb5b961c113bcb04ca420c47410596022594182 |
| DMZ | DIMETHYLZINC | 二甲基锌 | 544-97-8 | MethylzincZinc dimethylZinc methyl | pdf_6a8faacca882a39304796eef402a5436_6a33b7acef319cae52b9a3cf5b05a7727410596022594182 |
| DNA | DI-N-PROPYLAMINE | 二正丙胺 | 142-84-7 | N-Propyl-1-propanamine | pdf_6a8faacca882a39304796eef402a5436_57ec9e1c6b6dbd5207fd4ef112c3b4a87410596022594182 |
| DNB | M-DINITROBENZENE | 间二硝基苯 | 99-65-0 |  | pdf_6a8faacca882a39304796eef402a5436_d9d15487d38e59d1d9c6232b2e52ecc27410596022594182 |
| DNC | DINITROCRESOL | 二硝基甲酚 | 534-52-1 |  | pdf_6a8faacca882a39304796eef402a5436_c047c1d885cdc2dc60d236d025a13a387410596022594182 |
| DNE | 2,5-DINITROPHENOL | 2,5-二硝基苯酚 | 329-71-5 | gamma-Dintrophenol2.5-DNP | pdf_6a8faacca882a39304796eef402a5436_60d019ba51fcee85bb749d6dad586e6f7410596022594182 |
| DNH | 2,6-DINITROPHENOL | 2,6-二硝基苯酚 | 573-56-8 | beta-Dinitrophenolo-o-DinitrophenolDNP | pdf_6a8faacca882a39304796eef402a5436_5346238ac103c7e84b96c39665db85637410596022594182 |
| DNL | 2,6-DINITROTOLUENE | 2,6-二硝基甲苯 | 606-20-2 | 2.6-DNTToluene, 2.6-dinitro- | pdf_6a8faacca882a39304796eef402a5436_b6625b7deb5b8482b067d6b613e839b77410596022594182 |
| DNO | O-DINITROBENZENE | 邻二硝基苯 | 528-29-0 | 1.2-Dinitrobenzeneo-Dinitrobenzol | pdf_6a8faacca882a39304796eef402a5436_9fe5059d21341de62e458b28559322f27410596022594182 |
| DNP | 2,4-DINITROPHENOL | 2,4-二硝基苯酚 | 51-28-5 |  | pdf_6a8faacca882a39304796eef402a5436_f0d374b769b95a0aa0336b45bb3886577410596022594182 |
| DNT | 2.4-DINITROANILINE | 2,4-二硝基苯胺 |  |  | pdf_6a8faacca882a39304796eef402a5436_e5bd872c12796ce9fed41206666785397410596022594182 |
| DNU | 3,4-DINITROTOLUENE | 3,4-二硝基甲苯 | 610-39-9 | 3.4-DNTToluene, 3,4-dinitr- | pdf_6a8faacca882a39304796eef402a5436_7b4c74b36f1abe76a2febc8bc74f78a47410596022594182 |
| DNY | DIISONONYL ADIPATE | 己二酸二异壬酯 | 33703-08-1 |  | pdf_6a8faacca882a39304796eef402a5436_306dccd7f1f071943b198cc2885af5e47410596022594182 |
| DNZ | P-DINITROBENZENE | 对二硝基苯 | 100-25-4 | 1,4-Dinitrobenzene | pdf_6a8faacca882a39304796eef402a5436_3c7b542ea83933671809fa562f4dddea7410596022594182 |
| DOA | DIOCTYL ADIPATE | 己二酸二辛酯（DOA） | 123-79-5 | Adicip acid, bis (2-ethyhexyl)esterAdipol 2HEHDi (2-ethyhexyl) adipateDOA | pdf_6a8faacca882a39304796eef402a5436_2b5a592590f9a407e79b47f024441d017410596022594182 |
| DOD | DODECENE | 十二烯 | 112-41-4 | Dodecene (non-linear)Propylene tetramerTetraproylene | pdf_6a8faacca882a39304796eef402a5436_185170110625755f863dd87810789b587410596022594182 |
| DOL | DODECYL PHENOL | 十二烷基苯酚 | 5284-29-7 |  | pdf_6a8faacca882a39304796eef402a5436_7e228a64c2ba74d820ff9f1c5a9b6a8a7410596022594182 |
| DOP | DIOCTYL PHTHALATE | 邻苯二甲酸二辛酯（DOP） | 117-84-0 | Di-(2-ethylhexyl) pithalateDOPBis-(2-Ethyhexyl)pithalateOctoilPhthalic acid, bis | pdf_6a8faacca882a39304796eef402a5436_4bcda298b1a8399a996cf9de99e5d4447410596022594182 |
| DOS | DODECYL DIPHENYL ETHER DISULFONATE SOLUTION | 十二烷基二苯醚二磺酸盐溶液 |  | Dodecyl diphenyl ethersuffonate, disodium salt,aqueous solutionDowfax 2A1 | pdf_6a8faacca882a39304796eef402a5436_0335c4db55b84a0e72b315f4e7b12ea67410596022594182 |
| DOX | 1,4-DIOXANE | 1,4-二氧六环 | 123-91-1 | Di(ethylene oxide)Dioxanep-Dioxane | pdf_6a8faacca882a39304796eef402a5436_101c82c39d432d21f2c921cd60f00f797410596022594182 |
| DPA | DIBUTYL PHTHALATE | 邻苯二甲酸二丁酯（DBP） | 84-74-2 | Butyl phthalateDBPPhthalic acid, dibutyl esterRC plasticizer DBPWiticizer 300 | pdf_6a8faacca882a39304796eef402a5436_40ef0bf1261cfbec4f7493f3826a28de7410596022594182 |
| DPB | 1.1-DICHOROPROPANE | 1,1-二氯丙烷 |  |  | pdf_6a8faacca882a39304796eef402a5436_bfbcb247c510f48bd03fc516c31dcb667410596022594182 |
| DPC | 1,3-DICHOROPROPANE | 1,3-二氯丙烷 | 142-28-9 | Trimethylene chlorideTrimethylene dichloride | pdf_6a8faacca882a39304796eef402a5436_da08f97b0fa95d1f1923cfe43de4e0d57410596022594182 |
| DPD | DIPHENYLDICHLOROSILANE | 二苯基二氯硅烷 | 80-10-4 | DichlorodiphenylisaneDichlorodiphenylsilcaneDiphenylsilicon dichloride | pdf_6a8faacca882a39304796eef402a5436_b3f51490f5469b3390bc1f8eff9589457410596022594182 |
| DPE | DIPHENYL ETHER | 二苯醚 | 101-84-8 |  | pdf_6a8faacca882a39304796eef402a5436_3fc16044d521b21999991bbd41eea12b7410596022594182 |
| DPF | 2,3-DICHOROPROPENE | 2,3-二氯丙烯 | 78-88-6 |  | pdf_6a8faacca882a39304796eef402a5436_dfac0e42025e8223e7ef2e4e2135ce957410596022594182 |
| DPG | DIPROPYLENE GLYCOL | 二丙二醇 | 25265-71-8 |  | pdf_6a8faacca882a39304796eef402a5436_d6ef8e8a5a04e4ef2a389b5b30bdcd087410596022594182 |
| DPH | DIETHYL PHTHALATE | 邻苯二甲酸二乙酯（DEP） | 84-66-2 | 1.2-Benzenedicarboxylic acid, diethyl esterEthyl phthalatePhthalic acid, diethyl | pdf_6a8faacca882a39304796eef402a5436_cfc141fda11295df7a3911e591b10b707410596022594182 |
| DPI | DIMETHYL HYDROGEN PHOSPHITE | 亚磷酸二甲酯 | 868-85-9 |  | pdf_6a8faacca882a39304796eef402a5436_68dc7e4a5c573d48445295c49b4edb987410596022594182 |
| DPM | DIPHENYLMETHANE DIISOCYANATE | 二苯基甲烷二异氰酸酯（MDI） | 101-68-8 |  | pdf_6a8faacca882a39304796eef402a5436_4633372b3ab27b03e69c546a449d4e0a7410596022594182 |
| DPN | DIPENTENE | 二戊烯 | 138-86-3 | delta-1,8-Terpodienelimonenep-Methina-1,8-dienep-PhelandreneTerpinene | pdf_6a8faacca882a39304796eef402a5436_6b63d5ffa4d144cbbc32c22ba4310df07410596022594182 |
| DPO | DIBENZOYL PEROXIDE | 过氧化二苯甲酰（BPO） | 94-36-0 | Benzoyl peroxideBenzoyl superoxideBPBPOLucidolOxylite | pdf_6a8faacca882a39304796eef402a5436_afe71010d02bb16ff18d328eeef547287410596022594182 |
| DPP | 1,2-DICHOROPROPANE | 1,2-二氯丙烷 | 78-87-5 | DichloropropanePropylene dichloride | pdf_6a8faacca882a39304796eef402a5436_7347a7d44e358e0562d0836385cf5bf67410596022594182 |
| DPT | DICYCLOPENTADIENE | 二环戊二烯 | 77-73-6 |  | pdf_6a8faacca882a39304796eef402a5436_df6b7bc806f9215e105815184a1c5b5c7410596022594182 |
| DPU | 1,3-DICHOROPROPENE | 1,3-二氯丙烯 | 542-75-6 | DichloropropeneTeone | pdf_6a8faacca882a39304796eef402a5436_9c91ecbb6e98886d4eaed2e2483346ae7410596022594182 |
| DPY | DIPROPYLENE GLYCOL METHYL ETHER | 二丙二醇甲醚 | 34590-94-8 | Dipropylene glycol monomethyliotherDowanol-50BDowanol-50BDowanol DPMUcar solvent | pdf_6a8faacca882a39304796eef402a5436_22630f051862cf20a9d67ba897180e017410596022594182 |
| DSA | DODECYLBENZENESULFONIC ACID | 十二烷基苯磺酸 |  | Conco SA 597Laurybenzenesulfonic acidNacconol 988 A | pdf_6a8faacca882a39304796eef402a5436_6e5e1ada9505e3eef9fefbd42494c0417410596022594182 |
| DSD | DODECYL SULFATE, DIETHANOLAMINE SALT | 十二烷基硫酸二乙醇胺盐 |  | Diethanolamine lauryl sulfatesolutionLauryl sulfate, dianholaminesalt solution | pdf_6a8faacca882a39304796eef402a5436_806ed75704e5731a07cb02101b1e300d7410596022594182 |
| DSE | DIMETHYL SUCCINATE | 丁二酸二甲酯 | 106-65-0 |  | pdf_6a8faacca882a39304796eef402a5436_11ef344fab1f67a713dc011c02624b217410596022594182 |
| DSF | DIMETHYL SULFATE | 硫酸二甲酯 | 77-78-1 | Methyl sulfate | pdf_6a8faacca882a39304796eef402a5436_24d7a0c91f9960a3adb52761a4db32857410596022594182 |
| DSL | DIMETHYL SULFIDE | 二甲硫醚 | 75-18-3 |  | pdf_6a8faacca882a39304796eef402a5436_dff2da1794736053f401d81f78c934667410596022594182 |
| DSM | DODECYL SULFATE, MAGNESIUM SALT | 十二烷基硫酸镁 | 3097-08-3 | Lauryl magnesium sulfateLauryl sulfate, magnesium saltMagnesium dodecyl sulfateM | pdf_6a8faacca882a39304796eef402a5436_2a89a86bcceefb9b3f9f05f398d88b747410596022594182 |
| DSR | DISTILLATES: STRAIGHT RUN | 直馏馏分油 |  | Petroleum distillateStraight run gasoline | pdf_6a8faacca882a39304796eef402a5436_1a21184cba9630eef4303493a7e031a87410596022594182 |
| DSS | DIOCTYL SODIUM SULFOSUCCINATE | 磺基琥珀酸二辛酯钠 | 1639-66-3 | Aerosol surfactantAlrowet D65DI-(2-ethyhexyl) suffosucinate, sodium saltBis-(2-E | pdf_6a8faacca882a39304796eef402a5436_7b8d5f7cc8a3ba24b5fb32b83de69d537410596022594182 |
| DST | DODECYL SULFATE, TRIETHANOLAMINE SALT | 十二烷基硫酸三乙醇胺盐 |  | Lauryl sulfate, triethanolaminesaltTriethanolamine lauryl sulfate | pdf_6a8faacca882a39304796eef402a5436_df79aed46fe8ac95e6d12cf35445957a7410596022594182 |
| DSU | DIETHYL SULFATE | 硫酸二乙酯 | 64-67-5 | Diethyl sulphateEthyl sulfateSulfuric acid, diethyl ester | pdf_6a8faacca882a39304796eef402a5436_7c333096c0ac9c18153dbf868a10ce667410596022594182 |
| DSZ | DIAMMONIUM SALT OF ZINC EDTA | 锌EDTA二铵盐 |  |  | pdf_6a8faacca882a39304796eef402a5436_101acf9516c4fca051877033df993fdf7410596022594182 |
| DTC | DODECYLTRICHLOROSILANE | 十二烷基三氯硅烷 | 4484-72-4 |  | pdf_6a8faacca882a39304796eef402a5436_5b0a2cffa29af4efe7b99712443413f97410596022594182 |
| DTE | DICHLOROTETRAFLUOROETHANE | 二氯四氟乙烷 | 76-14-2 |  | pdf_6a8faacca882a39304796eef402a5436_11f1c6dfb4afe166472d54df042e6f977410596022594182 |
| DTH | DOWTHERM | 道氏导热油 | 8004-13-5 | Diphenyl-diphenyl ether mixtureDowtherm A | pdf_6a8faacca882a39304796eef402a5436_8cea21b3388cec68be794f1d90656c2f7410596022594182 |
| DTL | DIMETHYL PHTHALATE | 邻苯二甲酸二甲酯（DMP） | 131-11-3 |  | pdf_6a8faacca882a39304796eef402a5436_67914a861f177408d0b5abcba983c45f7410596022594182 |
| DTM | 4,4'-DICHORO-ALPHA-TRICHOROMETHYL BENZHYDROL | 4,4'-二氯-α-三氯甲基二苯甲醇 |  | 1.1-Bis(p-Chlorophenol)2.2,2-trichloroethanolDI-(p-chlorophenyl)trichloromethylc | pdf_6a8faacca882a39304796eef402a5436_e1f4e8c13ed88f45c22d41c833465ed07410596022594182 |
| DTN | DEMETON | 内吸磷 | 8065-48-3 | O.O(dethyl-o(and J5)-J2-(ethythio)ethyl(phosphorothioatesSystox and isosystol mi | pdf_6a8faacca882a39304796eef402a5436_4ca531707b548fd8fa04da25aa472dd97410596022594182 |
| DTP | DITRIDECYL PHTHALATE | 邻苯二甲酸双十三酯 | 119-06-2 |  | pdf_6a8faacca882a39304796eef402a5436_36b417ad84b1b19493a030a7fd233e3e7410596022594182 |
| DTS | DEXTROSE SOLUTION | 葡萄糖溶液 | 50-99-7 |  | pdf_6a8faacca882a39304796eef402a5436_95bd34d7f2be78e03db687f6e0b4d8517410596022594182 |
| DTT | 2,4-DINITROTOLUENE | 2,4-二硝基甲苯 | 121-14-2 | 2,4-DinitrotolulDNT1-Methyl-2, 4-diritrobenzene | pdf_6a8faacca882a39304796eef402a5436_7e2c6cb2a09494a40d0788019cdc69517410596022594182 |
| DUP | DIUNDECYL PHTHALATE | 邻苯二甲酸双十一酯 | 39393-37-8 | 1.2-Benzenedicarboxylic acid,di-undecyl esterPhthalic acid, diundecyl esterSanti | pdf_6a8faacca882a39304796eef402a5436_9a22dc133af8104bf40b1e983cfe6b997410596022594182 |
| DUR | DURSBAN | 毒死蜱 | 2921-88-2 |  | pdf_6a8faacca882a39304796eef402a5436_60c52aec981c77dfd0d80492feb72fe07410596022594182 |
| DXN | N,N-DIMETHYLCYCLOHEXYLAMINE | N,N-二甲基环己胺 | 98-94-2 | Cyclohexylamine, n-dimethyln-Dimethylcyclohexamine | pdf_6a8faacca882a39304796eef402a5436_7e0075f10eb9ebffbeedef9e9a19fbfa7410596022594182 |
| DZN | DIAZINON | 二嗪磷 | 333-41-5 |  | pdf_6a8faacca882a39304796eef402a5436_97ee9d7a8173d5af5171febad2b08a347410596022594182 |
| DZP | DI-(P-CHLOROBENZOYL) PEROXIDE | 过氧化二（对氯苯甲酰） | 94-17-7 |  | pdf_6a8faacca882a39304796eef402a5436_13e8a8e09c40c195608f84034c448a807410596022594182 |
| EAA | ETHYL ACETOACETATE | 乙酰乙酸乙酯 | 141-97-9 | Acetoacetic acid, ethyl esterDiacetic etherEAAEthyl 3-oxobutanoate | pdf_6a8faacca882a39304796eef402a5436_d83076e3ae4e33023b31badfea00e4ba7410596022594182 |
| EAC | ETHYL ACRYLATE | 丙烯酸乙酯 | 140-88-5 | Acrylic acid, ethyl esterEthyl 2-propenoate | pdf_6a8faacca882a39304796eef402a5436_9d88e77cb41ea14de8817943c254ae357410596022594182 |
| EAD | ETHYLALUMINUM DICHLORIDE | 二氯化乙基铝 | 563-43-9 | Aluminum ethyl dichlorideEADC | pdf_6a8faacca882a39304796eef402a5436_c3fdd4bc966f5f94a55c5ec9fbf471457410596022594182 |
| EAI | 2-ETHYLHEXYL ACRYLATEEAl | 丙烯酸2-乙基己酯 |  | Acrylic acid, 2-ethyhexylester2-Ethyhexyl-2-propenoate | pdf_6a8faacca882a39304796eef402a5436_c826d3d5b95396688c25336547d460337410596022594182 |
| EAK | ETHYL AMYL KETONE | 乙基戊基酮 | 541-85-5 |  | pdf_6a8faacca882a39304796eef402a5436_d7dbb0a34cd61d86fdf69f6de47946627410596022594182 |
| EAL | ETHYL ALCOHOL | 乙醇 | 64-17-5 |  | pdf_6a8faacca882a39304796eef402a5436_cbb1ab21d3230c892ed59fea82aff4497410596022594182 |
| EAM | ETHYLAMINE | 乙胺 | 75-04-7 | AminoethaneMonoethylamine | pdf_6a8faacca882a39304796eef402a5436_cc9b3f9a08b97f6f58708c90340227de7410596022594182 |
| EAS | ETHYLALUMINUM SESQUICHLORIDE | 倍半氯化乙基铝 | 12075-68-2 |  | pdf_6a8faacca882a39304796eef402a5436_91268fb9f2f2314980924addc7da84207410596022594182 |
| EBA | N-ETHYL-N-BUTYLAMINE | N-乙基正丁胺 | 13360-63-9 |  | pdf_6a8faacca882a39304796eef402a5436_d324dec83e09913958e77cd0ea70e96e7410596022594182 |
| EBK | ETHYL BUTYL KETONE | 乙基丁基酮 | 106-35-4 |  | pdf_6a8faacca882a39304796eef402a5436_030f6f8a811738debb00d9aadf7f78a27410596022594182 |
| EBR | ETHYL BUTYRATE | 丁酸乙酯 | 105-54-4 | Butyric acid, ethyl esterEthyl butanoate | pdf_6a8faacca882a39304796eef402a5436_0e226dd7b48b39dca66f0e4b01eafc427410596022594182 |
| EBT | ETHYL BUTANOL | 乙基丁醇 | 97-95-0 |  | pdf_6a8faacca882a39304796eef402a5436_145755cdc72ef7ca184fe745526862a57410596022594182 |
| ECA | ETHYL CHLOROACETATE | 氯乙酸乙酯 | 105-39-5 | Chloroacetic acid, ethyl chloroacetateEthyl chloroethanateMonochlorethanoic acid | pdf_6a8faacca882a39304796eef402a5436_a868960f48e02643b733ce92cb8aeef67410596022594182 |
| ECC | N-ETHYLCYCLOHEXYLAMINE | N-乙基环己胺 | 5459-93-8 | Accelerator HXCcyclohexylamine, n-ethylN-CyclohexyllyamineN-Ethylcycloxhexanamin | pdf_6a8faacca882a39304796eef402a5436_9e0cb01012efd296876bc81dd5ee4f7e7410596022594182 |
| ECF | ETHYL CHLOROFORMATE | 氯甲酸乙酯 | 541-41-3 | Chloroformic acid, ethyl esterEthyl chlorocarbonate | pdf_6a8faacca882a39304796eef402a5436_cd4dccbc0a4291abf10bbd404772aa797410596022594182 |
| ECH | ETHYLENE CHOROHYDRIN | 氯乙醇 | 107-07-3 |  | pdf_6a8faacca882a39304796eef402a5436_0646eab596b2f133685c410b285bef3a7410596022594182 |
| ECL | ETHYL CHLORIDE | 氯乙烷 | 75-00-3 | ChloroethaneEther, hydrochloriMonchorethane | pdf_6a8faacca882a39304796eef402a5436_50b6fe52331bef45b5c94031b2e48bb47410596022594182 |
| ECS | ETHYLDICHLOROSILANE | 乙基二氯硅烷 | 1789-58-8 |  | pdf_6a8faacca882a39304796eef402a5436_a591c34e3f0ab2b0258d3cfdcac17cf07410596022594182 |
| ECT | ETHYL CHLOROTHIOFORMATE | 氯硫代甲酸乙酯 | 2941-64-2 | Ethyl chlorothiolformate | pdf_6a8faacca882a39304796eef402a5436_20a3b7ee07867276217061380660498a7410596022594182 |
| ECY | ETHYL CYCLOHEXANE | 乙基环己烷 | 1678-91-7 | Cyclohexyl ethane | pdf_6a8faacca882a39304796eef402a5436_66e9bec0b12c81330f0c12f00071dc617410596022594182 |
| EDA | ETHYLENEDIAMINE | 乙二胺 | 107-15-3 | 1.2-Diaminethane1.2-EthanediamineEthylenedamine (DownEthyleneamine 1302) | pdf_6a8faacca882a39304796eef402a5436_762400c694ed1e148da43eb8a31b8ec47410596022594182 |
| EDB | ETHYLENE DIBROMIDE | 1,2-二溴乙烷 | 106-93-4 | Bromofume 1.2-Dibromoethane sym-Dibromoethane Dow-fume 40 Ethylene bromide Glyco | pdf_6a8faacca882a39304796eef402a5436_cac282b59bbb536a9498032338b194b47410596022594182 |
| EDC | ETHYLENE DICHLORIDE | 1,2-二氯乙烷 | 107-06-2 |  | pdf_6a8faacca882a39304796eef402a5436_f8c98776cc4a80ce8c77695591ea19d27410596022594182 |
| EDR | ENDRIN | 异狄氏剂 | 72-20-8 | HexadrinMendrin | pdf_6a8faacca882a39304796eef402a5436_4bc25ea56f4236087199747a4f0895f47410596022594182 |
| EDT | ETHYLENEDIAMINE TETRACETIC ACID | 乙二胺四乙酸（EDTA） | 60-00-4 |  | pdf_6a8faacca882a39304796eef402a5436_bbcf3b8d0bbbcbf4d00065754e87abce7410596022594182 |
| EEA | 2-ETHOXYETHYL ACETATE | 2-乙氧基乙基乙酸酯 | 111-15-9 |  | pdf_6a8faacca882a39304796eef402a5436_ebcc62f1b1acdfebcaf6b66e8256fdc87410596022594182 |
| EEE | ETHYLENE GLYCOL DIETHYL ETHER | 乙二醇二乙醚 | 629-14-1 | 1.2-DiethoxyethaneDiethyl &quot cellosolove&quot | pdf_6a8faacca882a39304796eef402a5436_5166d8277d0b94fbdb7f3809fe7a8c957410596022594182 |
| EEO | 2-ETHOXYETHANOL | 2-乙氧基乙醇 | 110-80-5 |  | pdf_6a8faacca882a39304796eef402a5436_d373532d9e84aa877a4a59fb16080fdb7410596022594182 |
| EEP | ETHYL-3-ETHOXYPROPIONATE | 3-乙氧基丙酸乙酯 | 763-69-9 | Ethoxy propionic acid, ethylesterEthyl beta-ethoxypropionatePropronic acid, 3-et | pdf_6a8faacca882a39304796eef402a5436_9e879d8315e59a3e59ff79ab329c03e77410596022594182 |
| EET | ETHYL ETHER | 乙醚 | 60-29-7 | Anesthesia etherAnesthetic etherDiethyl etherDiethyl oxideEtherEthoxyethane | pdf_6a8faacca882a39304796eef402a5436_be98f7ed37c6768aa5b0eb3abbfdb3437410596022594182 |
| EFM | ETHYL FORMATE | 甲酸乙酯 | 109-94-4 |  | pdf_6a8faacca882a39304796eef402a5436_ed99ac3d4346106153312317147a69567410596022594182 |
| EGA | ETHYLENE GLYCOL MONOETHYL ETHER ACETATE | 乙二醇单乙醚乙酸酯 | 111-15-9 | Cellosolve acetate2-Ethoxyethyl ether acetateGlycol monoethyl ether acetatePoly- | pdf_6a8faacca882a39304796eef402a5436_d81d6711b0dc7703990af751b385948e7410596022594182 |
| EGB | ETHYLENE GLYCOL DIBUTYL ETHEREGB|CAUTIONARY RESPONSE INFORMATION||||---|---|---||Common Synonyms|Liquid|Colorless||1.2-DibutoxyethaneDibutyl cellosolveEthane, 1,2-dibutoxyEther ethylene glycol dibutyl||||Keep people away.Call fire department.Notify local health and pollution control agen | 乙二醇二丁醚 |  |  | pdf_6a8faacca882a39304796eef402a5436_0c5258f3e8c0b4b31f1616c8156929857410596022594182 |
| EGD | ETHYLENE GLYCOL DIMETHYL ETHER | 乙二醇二甲醚 | 110-71-4 |  | pdf_6a8faacca882a39304796eef402a5436_879713576df009c578bceffec6caee2f7410596022594182 |
| EGE | ETHYLENE GLYCOL MONOETHYL ETHER | 乙二醇单乙醚 | 110-80-5 |  | pdf_6a8faacca882a39304796eef402a5436_e15d351191bdcda8e775647562725e837410596022594182 |
| EGI | ETHYLENE GLYCOL ISOPROPYL ETHER | 乙二醇异丙醚 | 109-59-1 |  | pdf_6a8faacca882a39304796eef402a5436_880c473872042ebc5cf18787d62889447410596022594182 |
| EGL | ETHYLENE GLYCOL | 乙二醇 | 107-21-1 |  | pdf_6a8faacca882a39304796eef402a5436_f610633d0840da7746e02666c426ac157410596022594182 |
| EGM | ETHYLENE GLYCOL MONOBUTYL ETHER | 乙二醇单丁醚 | 111-76-2 |  | pdf_6a8faacca882a39304796eef402a5436_b446e96b08441c3b927c3d624b0677767410596022594182 |
| EGO | ETHYLENE GLYCOL ACETATE | 乙二醇乙酸酯 | 111-55-7 | 1.2-Ethanediol, monocateleEthylene glycol monocateteGlycol monocateteGlycol-mono | pdf_6a8faacca882a39304796eef402a5436_3221a469460e61f4c136bf2bcdc58b227410596022594182 |
| EGP | ETHYLENE GLYCOL PROPYL ETHER | 乙二醇丙醚 | 2807-30-9 | Ektasolve EPEthylene glycol monopropylether | pdf_6a8faacca882a39304796eef402a5436_fd93cccf61b62b03cc619ca151b104217410596022594182 |
| EGT | ETHYLENE GLYCOL METHYL ETHER ACETATE | 乙二醇甲醚乙酸酯 | 110-49-6 |  | pdf_6a8faacca882a39304796eef402a5436_59d5c2527dedf94be018cbca1c95b9777410596022594182 |
| EGY | ETHYLENE GLYCOL DIACETATE | 乙二醇二乙酸酯 | 111-55-7 |  | pdf_6a8faacca882a39304796eef402a5436_7b04af4dede97073869fd238ea8f61cf7410596022594182 |
| EHA | ETHYLHEXALDEHYDE | 乙基己醛 | 123-05-7 |  | pdf_6a8faacca882a39304796eef402a5436_e6e8de7d52130a7f5407c39a867d71937410596022594182 |
| EHC | 2-ETHYLHEXYL ACETATE | 乙酸2-乙基己酯 | 103-09-3 | Octyl acetate | pdf_6a8faacca882a39304796eef402a5436_343c31806104b02466ebacefcf8592ba7410596022594182 |
| EHE | ETHYL HEXYL PHTHALATE | 邻苯二甲酸乙基己酯 | 117-81-7 |  | pdf_6a8faacca882a39304796eef402a5436_eaf9cb3ec1697c32208db317e147e8487410596022594182 |
| EHM | 2-ETHYLHEXYLAMINE | 2-乙基己胺 | 104-75-6 | 1-Amino-2-ethylhexane2-Ethyl-1-hexyaminebeta-Ethylhexamine | pdf_6a8faacca882a39304796eef402a5436_31e6a420c854df37ac6b0d7f8bbdc67d7410596022594182 |
| EHO | 2-ETHYLHEXANOIC ACID | 2-乙基己酸 | 149-57-5 |  | pdf_6a8faacca882a39304796eef402a5436_094bb5d434f893ad011fdf03c7e897547410596022594182 |
| EHP | ETHOXYDIHYDROPYRAN | 乙氧基二氢吡喃 | 103-75-3 | 2-Ethoxy-3,4-dihydro-2h-pyran | pdf_6a8faacca882a39304796eef402a5436_0dc829008b456f6168d922a2f3d199857410596022594182 |
| EHT | ETHYL HEXYL TALLATE | 妥尔油酸乙基己酯 |  | Croplas EH | pdf_6a8faacca882a39304796eef402a5436_75b5b97c4259276782d9ced2dd365ab67410596022594182 |
| EHX | 2-ETHYL HEXANOL | 2-乙基己醇 | 104-76-7 | 2-Ethyl-1-hexanol2-Ethylhexyl alcohol | pdf_6a8faacca882a39304796eef402a5436_bab020d4d5b69a642d3c8145fbb63dc07410596022594182 |
| ELT | ETHYL LACTATE | 乳酸乙酯 | 97-64-3 |  | pdf_6a8faacca882a39304796eef402a5436_fa18313ddf3f75ee0f557cb39cf3e8887410596022594182 |
| EMA | ETHYLENE GLYCOL MONOBUTYL ETHER ACETATE | 乙二醇单丁醚乙酸酯 | 112-07-2 | 2-Butoxyethanol acetate2-Butoxyethyl&quot acetateButyl &quot cellosolve&quot ace | pdf_6a8faacca882a39304796eef402a5436_2047dc7b07de59a06b76600c4b145fe17410596022594182 |
| EMC | ETHYL MERCAPTAN | 乙硫醇 | 75-08-1 |  | pdf_6a8faacca882a39304796eef402a5436_d1ac81bef352d245553a58c3e596c7447410596022594182 |
| EME | ETHYLENE GLYCOL MONOMETHYL ETHER | 乙二醇单甲醚 | 109-86-4 | Dowanol EMGlycol monomethyl ether2-MethoxyethanolMethyl cellosolvePoly-solv EM | pdf_6a8faacca882a39304796eef402a5436_77508e8b9c67d0a71002b3fca63a092f7410596022594182 |
| EMN | N-ETHYL MORPHOLINE | N-乙基吗啉 | 100-74-3 | 4-Ethylmorpholine | pdf_6a8faacca882a39304796eef402a5436_12c924b5df77af4aa46518bf1b7735597410596022594182 |
| EMX | ETHYLENEDIAMINE | 乙二胺 | 107-15-3 | 1.2-Diaminethane1.2-EthanediamineEthylenedamine (DownEthyleneamine 1302) | pdf_6a8faacca882a39304796eef402a5436_b1b7037226e3dbcd24b11c8d195b60c37410596022594182 |
| ENB | ETHYLIDENE NORBORNENE | 乙叉降冰片烯 | 16219-75-3 | 5-Ethyl-2-ene1) hept-2-eneEthylidenenorbmyleneEthylidenenorcmhene | pdf_6a8faacca882a39304796eef402a5436_d2d2679cf25980ceb4c9b0dadfdc099f7410596022594182 |
| ENP | ETHOXYLATED NONYLPHENOL | 乙氧基化壬基酚 |  |  | pdf_6a8faacca882a39304796eef402a5436_aeef6fdae0d82692a87770fbd7deeee37410596022594182 |
| EOD | ETHOXYLATED DODECANOL | 乙氧基化十二醇 |  | Extingled dodecyl alcoholEthoxylated lauryl alcoholPoly (oxyethyl) dodecyl (ethe | pdf_6a8faacca882a39304796eef402a5436_f84d1eb08bfc8398d55e92ba57f24db17410596022594182 |
| EOP | ETHOXYLATED PENTADECANOL | 乙氧基化十五醇 |  | Ethoxylated pentadecylalcoholPoly(oxeythy) pentadecyl(etherTergitol nonionic 45- | pdf_6a8faacca882a39304796eef402a5436_a10951f3fadd23485c7797169e173a707410596022594182 |
| EOT | ETHOXYLATED TETRADECANOL | 乙氧基化十四醇 |  |  | pdf_6a8faacca882a39304796eef402a5436_b130a8391645d65c69f855ed03b2a05c7410596022594182 |
| EOX | ETHYLENE OXIDE | 环氧乙烷 | 75-21-8 | 1.2-EpoxythaneOxirane | pdf_6a8faacca882a39304796eef402a5436_7750341bef204a01e1d4a6772c4908877410596022594182 |
| EPA | 2-ETHYL-3-PROPYLACROLEIN | 2-乙基-3-丙基丙烯醛 | 645-62-5 | 2-Ethyl-2-hexenal2-Ethyl-3-propylacryaldehyde | pdf_6a8faacca882a39304796eef402a5436_7124850f07911b0f6907676fd15c1f177410596022594182 |
| EPC | EPICHLOROHYDRIN | 环氧氯丙烷 | 106-89-8 | 1-Chloro-2,3-epoxpropaneChloromothyloxianare3-Chloro-1, 2-propylene oxidegamma-C | pdf_6a8faacca882a39304796eef402a5436_1596bc4480b8a51ed10d39e78ee8a4ba7410596022594182 |
| EPD | ETHYL PHOSPHONOTHIOIC DICHLORIDE | 乙基硫代膦酰二氯 | 993-43-1 |  | pdf_6a8faacca882a39304796eef402a5436_12efcda3b56f7ebcfe1c437df8cfc9d87410596022594182 |
| EPE | ETHYLENE GLYCOL PHENYL ETHER | 乙二醇苯醚 | 122-99-6 |  | pdf_6a8faacca882a39304796eef402a5436_160623c1181073bc3322cac8e1257c327410596022594182 |
| EPL | ETHYLPHENOL | 乙基苯酚 | 90-00-6 |  | pdf_6a8faacca882a39304796eef402a5436_4500e4e9958e435769f136686ca18c4e7410596022594182 |
| EPP | ETHYL PHOSPHORODICHLORIDATE | 乙基磷酰二氯 | 1498-51-7 | Ethyl dichlorophosphatePhosphorodichloric acid, ethlyester | pdf_6a8faacca882a39304796eef402a5436_5edf6774357cb825e83fd92cfbffa8967410596022594182 |
| EPR | ETHYL PROPIONATE | 丙酸乙酯 | 105-37-3 | Propanoc acid, ethyl ester | pdf_6a8faacca882a39304796eef402a5436_bbf9c597a0748e2959380461ff253cd27410596022594182 |
| EPS | ETHYLPHENYLDICHLOROSILANE | 乙基苯基二氯硅烷 | 1125-27-5 |  | pdf_6a8faacca882a39304796eef402a5436_1add7da5cfae68f74655dc7a411190f07410596022594182 |
| ESC | ETHYL SILICATE | 硅酸乙酯 | 78-10-4 | Ethyl orthosilicateEthyl silicate 40Ethyl silicate condensedSilbondTetraethyl or | pdf_6a8faacca882a39304796eef402a5436_ac2ddee052c538749610f382ae4a530d7410596022594182 |
| ESF | ENDOSULFAN | 硫丹 | 115-29-7 | ChlorthepinCyclodanMalixThiodan | pdf_6a8faacca882a39304796eef402a5436_81f0d0beab8c8ab5b5e4508a5d1d3e8c7410596022594182 |
| ETA | ETHYL ACETATE | 乙酸乙酯 | 141-78-6 |  | pdf_6a8faacca882a39304796eef402a5436_39862baf29a1b51a07ced5233a3683f27410596022594182 |
| ETB | ETHYLBENZENE | 乙苯 | 100-41-4 | EBPhenylethane | pdf_6a8faacca882a39304796eef402a5436_22fdaefe9b233f762d01773bd5f2baaa7410596022594182 |
| ETC | ETHYLENE CYANOHYDRIN | 氰乙醇 | 109-78-4 | 2-CyanethanoiGlycol cyanohrdinHydroacrylonitrile1-Hydroxy-2-cyanoethane3-Hydroxp | pdf_6a8faacca882a39304796eef402a5436_7ee525cdf47df59effff2a66b1ee52ed7410596022594182 |
| ETD | ETHOXYLATED TRIDECANOL | 乙氧基化十三醇 |  | Ethoxylated tridecyl alcoholPoly(oxyethyl) tridecyl etherTergolol nonionic 3-A-6 | pdf_6a8faacca882a39304796eef402a5436_3cee068520e13996f9eb277da28a4c1c7410596022594182 |
| ETE | 2-ETHYL TOLUENE | 2-乙基甲苯 | 611-14-3 | 1-Ethyl-2-methylbenzeneo-Ethylmethy/benzeneo-Ethyltolueneno-Methylylebenzene | pdf_6a8faacca882a39304796eef402a5436_ff26527bfa2efe027f4795699fb03e567410596022594182 |
| ETG | ETHOXY TRIGLYCOL | 乙氧基三甘醇 | 112-50-5 | Dowanol TEEthoxytriethylene glycolTriethylene glycol monotyllytherTriglycol mono | pdf_6a8faacca882a39304796eef402a5436_d93d0718a8b001964697e0adf2f6b7c97410596022594182 |
| ETH | ETHANE | 乙烷 | 74-84-0 | Methylmethane | pdf_6a8faacca882a39304796eef402a5436_2cb544b480e628780ec1aa1f104fbeb97410596022594182 |
| ETI | ETHYLENEIMINE | 氮丙啶 | 151-56-4 | Azirine | pdf_6a8faacca882a39304796eef402a5436_852172e94becd1e0af1cbb226ed3c0047410596022594182 |
| ETL | ETHYLENE | 乙烯 | 74-85-1 | EtheneOleffant gas | pdf_6a8faacca882a39304796eef402a5436_fae45973b6648ddf137bfd311c04e3627410596022594182 |
| ETM | ETHYL METHACRYLATE | 甲基丙烯酸乙酯 | 97-63-2 |  | pdf_6a8faacca882a39304796eef402a5436_87bb54a78176d4e40d3fcc7943cd419b7410596022594182 |
| ETN | ETHYL NITRITE | 亚硝酸乙酯 | 109-95-5 |  | pdf_6a8faacca882a39304796eef402a5436_eb8550d716558299ed3dc90c7dd1342a7410596022594182 |
| ETO | ETHION | 乙硫磷 | 563-12-2 | DiethionNA. 12 40Nialate | pdf_6a8faacca882a39304796eef402a5436_c7fd0e4f38e63d2a7ed5f8794a74e9727410596022594182 |
| ETS | ETHYLTRICHLOROSILANE | 乙基三氯硅烷 | 115-21-9 | Ethyl silicon trichlorideTrichlorethyl silaneTrichloroethyl silicone | pdf_6a8faacca882a39304796eef402a5436_1822668ee15462f9ba0a5ad33e65db6e7410596022594182 |
| EVO | EPOXIDIZED VEGETABLE OILS | 环氧植物油 |  | Drying oil epoxidesEpoxidized drying oilsEpoxidized oils | pdf_6a8faacca882a39304796eef402a5436_c15e8d7e52e2366fb1ea0f3818f25f3e7410596022594182 |
| FAC | FERRIC AMMONIUM CITRATE | 柠檬酸铁铵 | 1185-57-5 | Ammonium ferric citrateFerric ammonium citrate, brownFerric ammonium citrate, gr | pdf_6a8faacca882a39304796eef402a5436_c90ba41eee0a4c830c88c5435dc9659a7410596022594182 |
| FAL | FURFURYL ALCOHOL | 糠醇 | 98-00-0 | 2-FurancarboliFurfuralcohol2-Furycarbinol2-Hydroxymethylfuran | pdf_6a8faacca882a39304796eef402a5436_2dae978cca71cb971d3a9af3cb0952ba7410596022594182 |
| FAM | FORMAMIDE | 甲酰胺 | 75-12-7 |  | pdf_6a8faacca882a39304796eef402a5436_e24c48f2c8445f996d9dd4cfd80417967410596022594182 |
| FAN | 2-FLUOROANILINE | 2-氟苯胺 | 348-54-9 | 1-Amino-2-fluorobenzeneo-Fluoroaniline2-Fluorobenzamine2-Fluorophenylamine | pdf_6a8faacca882a39304796eef402a5436_7c2cc1e284727a27e8f28247a0628a7c7410596022594182 |
| FAO | FERRIC AMMONIUM OXALATE | 草酸铁铵 | 14221-47-7 | Amromium ferric oxalatetrihydrateAmmonium trioxalatoferrate(III)trihydrate | pdf_6a8faacca882a39304796eef402a5436_eddaa9343d832c969d807e50725690777410596022594182 |
| FAS | FERROUS AMMONIUM SULFATE | 硫酸亚铁铵 | 10045-89-3 | Ammonium ferrous sulfateFerrous ammonium sulfatehexahydrateIron ammonium sulfate | pdf_6a8faacca882a39304796eef402a5436_eb84f8b2015e36874d94d5deeb3d8bd27410596022594182 |
| FCL | FERRIC CHLORIDE | 氯化铁 | 7705-08-0 | Ferric chloride, anhydrousFerric chloride, hexahydrateIron III chlorideIron perc | pdf_6a8faacca882a39304796eef402a5436_afbe86bca9fac3b21804e10dcfdc2af17410596022594182 |
| FCP | FERRIC GLYCEROPHOSPHATE | 甘油磷酸铁 | 1301-70-8 |  | pdf_6a8faacca882a39304796eef402a5436_067f039f68cb734cc16a2d109417e8e47410596022594182 |
| FEC | FERROUS CHLORIDE | 氯化亚铁 | 7758-94-3 | Ferrous chloride tetrahydrateIron dichlorideIron dichloride | pdf_6a8faacca882a39304796eef402a5436_5e5021ef4df67734c27759ce0c6deff17410596022594182 |
| FFA | FURFURAL | 糠醛 | 98-01-1 | Fural2-FuraldehydeFural/pyromucic aldehydeFurfuraldehydeFurfurolePyromucic aldeh | pdf_6a8faacca882a39304796eef402a5436_a7986445bc29151e1f50dba3148024f87410596022594182 |
| FFB | FERROUS FLUOROBORATE | 氟硼酸亚铁 |  | Ferrous borofluoride | pdf_6a8faacca882a39304796eef402a5436_7d487e7c44c5dd2eac79a7890f7d6db87410596022594182 |
| FFX | FERRIC FLUORIDE | 氟化铁 | 7783-50-8 | Iron fluoride | pdf_6a8faacca882a39304796eef402a5436_2958d8c5a89a0c4439d34c2c46d62b897410596022594182 |
| FLA | 4-FLUOROANILINE | 4-氟苯胺 | 371-40-4 | 1-Amino-4-fluorobenzene4-Fluorobenzamine4-Fluorophenylamine | pdf_6a8faacca882a39304796eef402a5436_0b6de43b35e06f5c55585ac9511b92937410596022594182 |
| FLB | FLUOROBENZENE | 氟苯 | 462-06-6 | Benzene fluorideMFBMonofluorobenzenePhenyl fluoride | pdf_6a8faacca882a39304796eef402a5436_ac0bf67ca25ab55fbc03b2798222fd567410596022594182 |
| FLT | 2-FLUOROTOLUENE | 2-氟甲苯 | 95-52-3 | 1-Fluoro-2-methylbenzane2-Fluoro-1-methylbenzane1-Methyl-2-fluorobenzeneo-Tolyl  | pdf_6a8faacca882a39304796eef402a5436_a1daeae294703211ac22f6c68a0815fc7410596022594182 |
| FMA | FORMIC ACID | 甲酸 | 64-18-6 | Formylic acidMethanolic acid | pdf_6a8faacca882a39304796eef402a5436_8ac526aa65c792e6075656169039ab107410596022594182 |
| FMS | FORMALDEHYDE SOLUTION | 甲醛溶液 | 50-00-0 |  | pdf_6a8faacca882a39304796eef402a5436_fa41e1fab7b7170af59a5fa2d53594347410596022594182 |
| FNT | FERRIC NITRATE | 硝酸铁 | 10421-48-4 | Ferric nitrate nonahyrateNitric acid, iron(III) salt | pdf_6a8faacca882a39304796eef402a5436_2efd7bdc14d016eb2f776087aaef38bc7410596022594182 |
| FOX | FERROUS OXALATE | 草酸亚铁 | 516-03-0 | Ferrous oxalate dihydrateIron protoxalateOxalic acid, ferrous salt | pdf_6a8faacca882a39304796eef402a5436_2de057fe03dbee94723533c39d9179627410596022594182 |
| FPS | FERROPHOSPHORUS | 磷化铁 |  |  | pdf_6a8faacca882a39304796eef402a5436_12acb84203358ccd46906e6b612e1e157410596022594182 |
| FRS | FERROUS SULFATE | 硫酸亚铁 | 7720-78-7 | CopperasGreen vitrioliron (bus) sulfateIron (bus) sulfateIron (vitriol) | pdf_6a8faacca882a39304796eef402a5436_20c04cac37e7f9ba82bf96939b71c7bd7410596022594182 |
| FSA | FLUOSULFONIC ACID | 氟磺酸 | 7789-21-1 | Fluorosulfonic acidFluorosulfonic acidReacts violently with water. Irritating mi | pdf_6a8faacca882a39304796eef402a5436_46b242b0c1b165ed46aa1ad5db7b45fc7410596022594182 |
| FSF | FERRIC SULFATE | 硫酸铁 | 10028-22-5 | Iron sesquisulifateIron (II) suffateIron tersulfate | pdf_6a8faacca882a39304796eef402a5436_ea59fb7d2ef86428b5c28a289034402d7410596022594182 |
| FSL | FLUOSILICIC ACID | 氟硅酸 | 16961-83-4 |  | pdf_6a8faacca882a39304796eef402a5436_e0001852379ad6180ec3d22d123090857410596022594182 |
| FSN | FERROSILICON | 硅铁 | 8049-17-0 |  | pdf_6a8faacca882a39304796eef402a5436_9565cd1a0a837b0233c807ea20c75e1b7410596022594182 |
| FTO | 3-FLUOROTOLUENE | 3-氟甲苯 | 352-70-5 | 1-Fluoro-3-methylbenzenem-Fluorotoluene1-Methyl-3-fluorobenzenum-Tolyl fluoride | pdf_6a8faacca882a39304796eef402a5436_d92cac2450948562dde7ba9b7787d4ea7410596022594182 |
| FTU | 4-FLUOROTOLUENE | 4-氟甲苯 | 352-32-9 | 1-Fluoro-4-methylbenzene4-Fluoro-1-methylbenzenep-Fluorotoluenep-Tolyl fluoride | pdf_6a8faacca882a39304796eef402a5436_f783fa523baeb99921f352ac6c82acfa7410596022594182 |
| FUM | FUMARIC ACID | 富马酸 | 110-17-8 |  | pdf_6a8faacca882a39304796eef402a5436_4059367aeba75b8a850e6579985ff9307410596022594182 |
| FUR | FURAN | 呋喃 | 110-00-9 | Divinylene oxideFurfuranOxacyclopentadieneOxoleTetrole | pdf_6a8faacca882a39304796eef402a5436_996d6ffcd7c730b23ae5fcfd35adb0567410596022594182 |
| FXX | FLUORINE | 氟 | 7782-41-4 |  | pdf_6a8faacca882a39304796eef402a5436_e04d0c05b87d5c0186684c05b5de258d7410596022594182 |
| GAC | GLYOXYLIC ACID (50% OR LESS) | 乙醛酸（≤50%） | 298-12-4 | Formyl formic acidOxacetic acidOxoethanoic acid | pdf_6a8faacca882a39304796eef402a5436_aa9212432499b38f4e3383502f7d62e37410596022594182 |
| GAK | GASOLINE BLENDING STOCKS: ALKYLATESGAK|CAUTIONARY RESPONSE INFORMATION||||||---|---|---|---|---||Common Synonyms|Common Synonyms|Watery liquid|Colorless|Gasoline odor||EvaculateKeep people away.Wear chemical protective suit with self-contained breathing apparatus.Shut off ignition sources | 汽油调合料（烷基化油） |  |  | pdf_6a8faacca882a39304796eef402a5436_1850a8b34d10feb79736bcdf7dbc50d77410596022594182 |
| GAT | GASOLINES: AUTOMOTIVE (<4.23G LEAD/GAL) | 车用汽油（含铅<4.23g/gal） |  | Motor spiritPetrol | pdf_6a8faacca882a39304796eef402a5436_183a069dfde0a9cfe25a9fa1bf439f4f7410596022594182 |
| GAV | GASOLINES: AVIATION (< 4.86G LEAD/GAL) | 航空汽油（含铅<4.86g/gal） |  |  | pdf_6a8faacca882a39304796eef402a5436_e0c29555737f8a5465acb613571e52fa7410596022594182 |
| GCM | GLYCIDYL METHACRYLATE | 甲基丙烯酸缩水甘油酯 | 106-91-2 | Glycidyl alpha-methyl acrylateMethacrylic acid, 2, 3-epoxypropyl ester | pdf_6a8faacca882a39304796eef402a5436_e012cee774ced1ac4f7a943d02e376c67410596022594182 |
| GCR | GLYCERINE | 甘油 | 56-81-5 |  | pdf_6a8faacca882a39304796eef402a5436_ec79a2d4190a2b37228e093491bd741a7410596022594182 |
| GCS | GASOLINES: CASINGHEAD | 凝析油汽油 |  | Natural gasoline | pdf_6a8faacca882a39304796eef402a5436_95cca3bf08a0aea03fd62a8cdafb3e017410596022594182 |
| GLA | GALLIC ACID | 没食子酸 | 149-91-7 | Gallic acid monohydrate3,4,5,Trihydroxybenzoic acid | pdf_6a8faacca882a39304796eef402a5436_317f6ba893c550a9632b93d0f5e940737410596022594182 |
| GOC | GAS OIL: CRACKED | 裂化瓦斯油 |  |  | pdf_6a8faacca882a39304796eef402a5436_d6312bfcdb1fd19b7dd91f64b2d8aa007410596022594182 |
| GOS | GLYOXAL | 乙二醛 | 107-22-2 |  | pdf_6a8faacca882a39304796eef402a5436_e5eec39c06f7d04f5b143d7a2496bb137410596022594182 |
| GPL | GASOLINES: POLYMER | 聚合汽油 |  |  | pdf_6a8faacca882a39304796eef402a5436_d3331db8ae2bfc8053c8ab7e47e500d07410596022594182 |
| GRF | GASOLINE BLENDING STOCKS: REFORMATES | 汽油调合料（重整油） |  |  | pdf_6a8faacca882a39304796eef402a5436_5f1cf1d1e1f1aa8ae92278823a7b7f517410596022594182 |
| GSR | GASOLINES: STRAIGHT RUN | 直馏汽油 |  |  | pdf_6a8faacca882a39304796eef402a5436_9d5d3311a68be2cab972d3c7543a9e687410596022594182 |
| GTA | GLUTARALDEHYDE SOLUTION | 戊二醛溶液 | 111-30-8 | 1.5.Pentanedial | pdf_6a8faacca882a39304796eef402a5436_4620c2e50f8a46bd9eaea6165ff891277410596022594182 |
| HAC | HEXADECYLTRIMETHYLAMMONIUM CHLORIDE | 十六烷基三甲基氯化铵 | 112-02-7 |  | pdf_6a8faacca882a39304796eef402a5436_e2d09f8d7f3ae4fbdeae414f5f7d7c667410596022594182 |
| HAE | HEXYL ACETATE | 乙酸己酯 | 142-92-7 | Acetic acid, hexyl ester1-Hexyl acetaten-Hexyl alcohol, acetateHexyl ethanoate | pdf_6a8faacca882a39304796eef402a5436_218d3ba8db5a1d56fbd0fdeafcd698ed7410596022594182 |
| HAI | 2-HYDROXYETHYL ACRYLATE | 丙烯酸2-羟乙酯 | 818-61-1 | HEA beta-Hydroxyethyl acrylate2-Hydroxyethyl 2-propenate | pdf_6a8faacca882a39304796eef402a5436_c3f515acd33df53d9804ad36e42e61de7410596022594182 |
| HAL | N-HEXALDEHYDE | 正己醛 | 66-25-1 |  | pdf_6a8faacca882a39304796eef402a5436_2a99978c8fb74faf3780752bb4ffd2647410596022594182 |
| HAS | HYDROXYLAMINE SULFATE | 硫酸羟胺 | 10039-54-0 | Oxammonium sulfate | pdf_6a8faacca882a39304796eef402a5436_42e16970e735e8252f8cd064c33968cc7410596022594182 |
| HBA | 2-HYDROXY-4-(METHYLTHIO)-BUTANOIC ACID | 2-羟基-4-甲硫基丁酸 | 583-91-5 |  | pdf_6a8faacca882a39304796eef402a5436_a0b830ad23f3eea7ceceeba266670d8f7410596022594182 |
| HBR | HYDROGEN BROMIDE | 溴化氢 | 10035-10-6 | Hydrobromic acid, anhydrousHydrogen bromide, anthydrous | pdf_6a8faacca882a39304796eef402a5436_e6fad40086d2f23d126af7095f3353777410596022594182 |
| HCB | HEXACHLOROBUTADIENE | 六氯丁二烯 | 87-68-3 | 1.3-Butadiene, 1,1,2,3,4,4-hexachloro-HCBDHexachloro-1,3-butadienePerchlorobutad | pdf_6a8faacca882a39304796eef402a5436_add0a79da4ea47df6142ca9e5b8c33ed7410596022594182 |
| HCC | HEXACHLOROCYCLOPENTADIENE | 六氯环戊二烯 | 77-47-4 | Perchlorocyclopentadiene | pdf_6a8faacca882a39304796eef402a5436_cd526b718fb8d34b5129bbf1a0fb13c07410596022594182 |
| HCE | HEXACHLOROETHANE | 六氯乙烷 | 67-72-1 |  | pdf_6a8faacca882a39304796eef402a5436_505d9dc6dff902e12d089bb968054ce87410596022594182 |
| HCL | HYDROCHLORIC ACID | 盐酸 | 7647-01-0 | Muriatic acid | pdf_6a8faacca882a39304796eef402a5436_67043e31fe73fcdadb31335cd29261667410596022594182 |
| HCN | HYDROGEN CYANIDE | 氰化氢（氢氰酸） | 74-90-8 | Hydrocyanic acidPrussc acid | pdf_6a8faacca882a39304796eef402a5436_dd363823302b44e7714d208566aa254b7410596022594182 |
| HCP | HEXACHLOROPHENE | 六氯酚 | 70-30-4 |  | pdf_6a8faacca882a39304796eef402a5436_b12e80474070c49af3805f1aca9a97127410596022594182 |
| HCZ | HEXACHLOROBENZENE | 六氯苯 | 118-74-1 | Benzene, hexachloro-Pentachlorophenyl chloridePerchlorobenzenePhenyl perchloryl | pdf_6a8faacca882a39304796eef402a5436_e7ffa1df0bf4e56191940d9aad3168607410596022594182 |
| HDA | HYDROXYLAMINE | 羟胺 | 7803-49-8 | Oxammonium | pdf_6a8faacca882a39304796eef402a5436_8664c97158ac6364ceb6999110712f047410596022594182 |
| HDC | HYDROGEN CHLORIDE | 氯化氢 | 7647-01-0 | Hydrochloric acid, anhydrous | pdf_6a8faacca882a39304796eef402a5436_b4fc966326aff95e7fec77877f0b4d1b7410596022594182 |
| HDQ | HYDROQUINONE | 对苯二酚 | 123-31-9 |  | pdf_6a8faacca882a39304796eef402a5436_68369b9a5a9a4839d38e1ad59d7123b07410596022594182 |
| HDS | HYDROGEN SULFIDE | 硫化氢 | 7783-06-4 | Sulfurethed hydrogenSulphurethed hydrogen | pdf_6a8faacca882a39304796eef402a5436_199b5a4c874f3abdd3bef19cdc59f84c7410596022594182 |
| HDZ | HYDRAZINE | 肼（联氨） | 302-01-2 |  | pdf_6a8faacca882a39304796eef402a5436_f3d67ed5c7c77d000948fb5e66328dbb7410596022594182 |
| HEP | HEPTANOIC ACID | 庚酸 | 111-14-8 | Enanthic acidHeptic acidn-Heptolic acidHexane carboxyic acid | pdf_6a8faacca882a39304796eef402a5436_2497512a540def3e1341157589a1d66f7410596022594182 |
| HFA | HYDROFLUORIC ACID | 氢氟酸 | 7664-39-3 |  | pdf_6a8faacca882a39304796eef402a5436_d91b4b0afcf2339f82cd61d135cdee807410596022594182 |
| HFS | HYDROFLUOROSILICIC ACID (25% OR LESS) | 氟硅酸（≤25%） | 16961-83-4 |  | pdf_6a8faacca882a39304796eef402a5436_674382f9dc015f8bed466d9aaf20a8877410596022594182 |
| HFX | HYDROGEN FLUORIDE | 氟化氢 | 7664-39-3 | Hydrofluoric acid, anithyrous | pdf_6a8faacca882a39304796eef402a5436_cdd1c97cf3cf59e3b941538e58123d457410596022594182 |
| HMD | HEXAMETHYLENEDIAMINE | 己二胺 | 124-09-4 | 1.6-Diaminehexane1.6-HexanedamineHMDA | pdf_6a8faacca882a39304796eef402a5436_9497a56f1f1ec81b0c39ff5e04d902e47410596022594182 |
| HMI | HEXAMETHYLENIMINE | 六亚甲基亚胺 | 111-49-9 | AzacycloheptaneHexahydrozepineHompiperidine | pdf_6a8faacca882a39304796eef402a5436_6167e96257409b8139156a75d4dce61e7410596022594182 |
| HMT | HEXAMETHYLENETETRAMINE | 六亚甲基四胺（乌洛托品） | 100-97-0 |  | pdf_6a8faacca882a39304796eef402a5436_bcc4fab078d81bf677cb1cd2212d53767410596022594182 |
| HPA | HYDROXYPROPYL ACRYLATE | 丙烯酸羟丙酯 | 25584-83-2 | 1.2-Propanedol-1-acrylatePropylene glycol monoacrylate | pdf_6a8faacca882a39304796eef402a5436_cf5a72f9f39c8adbb04dae437cfeccfc7410596022594182 |
| HPE | HEPTYL ACETATE | 乙酸庚酯 | 112-06-1 | Acetate C-7Acetic acid, heptyl esterHeptanyl acetate1-Heptyl acetaten-Heptyl ace | pdf_6a8faacca882a39304796eef402a5436_2d5ab1ca4c8f96e1359c80571e52a6d77410596022594182 |
| HPM | HYDROXYPROPYL METHACRYLATE | 甲基丙烯酸羟丙酯 | 27813-02-1 | 1.2-Propanediol 1-methacrylatePropylene glycolmonomethacrylate | pdf_6a8faacca882a39304796eef402a5436_1743837837ce0fedb6f6cce5b47f9ea37410596022594182 |
| HPO | HYDROGEN PEROXIDE | 过氧化氢 | 7722-84-1 | AlbonePeroxideSuperoxol | pdf_6a8faacca882a39304796eef402a5436_2489991961e12edf9750da2e505926e87410596022594182 |
| HPT | HEPTANE | 庚烷 | 142-82-5 | n-Heptane | pdf_6a8faacca882a39304796eef402a5436_2b1367487f3f4981b80909c1f98ec7f07410596022594182 |
| HSS | HEXADECYL SULFATE, SODIUM SALT | 十六烷基硫酸钠 | 1120-01-0 | Cetyl sodium sulfateSodium celly sulfate solution | pdf_6a8faacca882a39304796eef402a5436_3a87d98c15a4ae4315ea4382a09b7e1d7410596022594182 |
| HTC | HEPTACHLOR | 七氯 | 76-44-8 | E3314 1,4,5,6,7,8,8a-Heptachiorodiclycopentadiene Velsicol | pdf_6a8faacca882a39304796eef402a5436_01e873d0c619c2dd7a401322c3e8b8ee7410596022594182 |
| HTE | 1-HEPTENE | 1-庚烯 | 25339-56-4 |  | pdf_6a8faacca882a39304796eef402a5436_f7ab09f3a648164a145e2c6fd4f32c647410596022594182 |
| HTN | HEPTANOL | 庚醇 | 111-70-6 | Enanthic alcohol1-HeptanolHeptyl alcohol1-Hydroxyheptane | pdf_6a8faacca882a39304796eef402a5436_2a7a1ce9ca02dc9c6646cc2d91aa7b037410596022594182 |
| HXA | N-HEXANE | 正己烷 | 110-54-3 | Hexane | pdf_6a8faacca882a39304796eef402a5436_a96408748010ce51109ae538af8e5abf7410596022594182 |
| HXE | 1-HEXENE | 1-己烯 | 592-41-6 | alpha-HexeneHexylene | pdf_6a8faacca882a39304796eef402a5436_4d0212c698902dbc379a02703f3496f67410596022594182 |
| HXG | HEXYLENE GLYCOL | 己二醇 | 107-41-5 | 2-Methyl-2,4-pentanedicol | pdf_6a8faacca882a39304796eef402a5436_93d9fbc71118a6dcb9d748f39ff7cc567410596022594182 |
| HXN | 1-HEXANOL | 1-己醇 | 111-27-3 |  | pdf_6a8faacca882a39304796eef402a5436_1fe7882475406b645eae760b33546b997410596022594182 |
| HXO | HEXANOIC ACID | 己酸 | 142-62-1 | Butylacetic acid n-Caproic acid Capronic acid Hexacid 698 n-Hexic acid n-1680 (D | pdf_6a8faacca882a39304796eef402a5436_aa9161d19ec182fce063260114c950627410596022594182 |
| HXX | HYDROGEN | 氢 | 1333-74-0 | para-HydrogenLiquid hydrogen | pdf_6a8faacca882a39304796eef402a5436_e5e47e4a7438af7f6de02134446e929b7410596022594182 |
| IAA | ISOAMYL ALCOHOL | 异戊醇 | 123-51-3 | Fermentation amyI alcoholFusel oilIsobulycarbinolIsopentyyl alcohol3-Methyl-1-bu | pdf_6a8faacca882a39304796eef402a5436_e560a69f366b81b11fe8315c09baf0c87410596022594182 |
| IAC | ISOPROPYL ACETATE | 乙酸异丙酯 | 108-21-4 | Acetic acid, isopropyl ester2-Propyl acetate | pdf_6a8faacca882a39304796eef402a5436_5d8db556d03b80eb69f51e17c7cfba177410596022594182 |
| IAI | ISODECYL ACRYLATElAl | 丙烯酸异癸酯 |  |  | pdf_6a8faacca882a39304796eef402a5436_459a731567c34d82094429c34a9669507410596022594182 |
| IAL | ISOBUTYL ALCOHOL | 异丁醇 | 78-83-1 | Fermentation butyl alcoholIsobutanoliscoprycarbinol2-Methyl-1-propanol | pdf_6a8faacca882a39304796eef402a5436_e9f1d723327548397fb5cf387a1e82ad7410596022594182 |
| IAM | ISOBUTYLAMINE | 异丁胺 | 78-81-9 | 1-Amino-2-methylpropaneiso-ButylamineMonoisobutylamine | pdf_6a8faacca882a39304796eef402a5436_3944ee4f83c9173235824e6a9305a78a7410596022594182 |
| IAT | ISOAMYLACETATE | 乙酸异戊酯 | 123-92-2 | Banana oilIsoamyl ethanateIsopently acetatePear oil | pdf_6a8faacca882a39304796eef402a5436_6fe09677d1b35b4b5b0cf91b0abfa7547410596022594182 |
| IBA | ISOBUTYL ACETATE | 乙酸异丁酯 | 110-19-0 | Acetic acid, isobulyl ester2-Methyl-1-propyl acetatebeta-Methylpropyl ethanace | pdf_6a8faacca882a39304796eef402a5436_bb313834478f24e8c8dfe7c9e36dba247410596022594182 |
| IBL | ISOBUTYLENE | 异丁烯 | 115-11-7 | Isobutene2-Methylpropene | pdf_6a8faacca882a39304796eef402a5436_0ebd4aad43c7e4869534e55cbb10899b7410596022594182 |
| IBN | ISOBUTYRONITRILE | 异丁腈 | 78-82-0 |  | pdf_6a8faacca882a39304796eef402a5436_f689df38c0a7a4c5ec85bdc07409d2877410596022594182 |
| IBR | ISOBUTYRIC ACID | 异丁酸 | 79-31-2 | Dimethylacetic acidIsopropylformic acid2-Methylpropanic acidalpha-Methylpropioni | pdf_6a8faacca882a39304796eef402a5436_2caddf64b968fe97bf90f7c3f253e47f7410596022594182 |
| IBT | ISOBUTANE | 异丁烷 | 75-28-5 | 2-Methyl/propane | pdf_6a8faacca882a39304796eef402a5436_c992e05f4344434f91b8fca642e2a60f7410596022594182 |
| IDA | ISODECALDEHYDE | 异癸醛 | 1321-89-7 | Isodecaldehyde, mixed isomersTrimethylheptanals | pdf_6a8faacca882a39304796eef402a5436_32de1ef77f9e443c5dac42a7d83ef8097410596022594182 |
| IGE | ISOPROPYL GLYCIDYL ETHER | 异丙基缩水甘油醚 | 4016-14-2 | Glycdyl isopropyl etherIsopropyl epoxypropy ether | pdf_6a8faacca882a39304796eef402a5436_c21260bf71d8221a6650206c6e5e22147410596022594182 |
| IHA | ISOHEXANE | 异己烷 | 107-83-5 | 2-Methylpentane | pdf_6a8faacca882a39304796eef402a5436_be915bf8c63f15c50848f500a65c767d7410596022594182 |
| IOA | ISOOCTYL ALCOHOL | 异辛醇 | 1653-40-3 | Dimethyl-1-hexanolsm6-Methyl-1-heptanolOxo octyl alcohol | pdf_6a8faacca882a39304796eef402a5436_3991339e1920cfaf84bbef685ad75ee37410596022594182 |
| IOC | ISOOCTALDEHYDE | 异辛醛 |  |  | pdf_6a8faacca882a39304796eef402a5436_eb0cb399911d3f6efb03927f7ac2dfa37410596022594182 |
| IPA | ISOPROPYL ALCOHOL | 异丙醇 | 67-63-0 | DimethylcarbinolIsopropanolPetrohol2-Propanolsec-Propyl alcoholRubbing alcohol | pdf_6a8faacca882a39304796eef402a5436_3cce8580ff88a2bf3c094a9783d542ae7410596022594182 |
| IPC | ISOPROPYL PERCARBONATE | 过氧化碳酸异丙酯 | 105-64-6 | Disisopropyl peroxbonatoneDisisopropyl peroxydicarbonateIsopropyl peroxydicarbon | pdf_6a8faacca882a39304796eef402a5436_117b263d7c3efa8ba0a460e798710b2d7410596022594182 |
| IPD | ISOPHORONE DIISOCYANATE | 异佛尔酮二异氰酸酯（IPDI） | 4098-71-9 |  | pdf_6a8faacca882a39304796eef402a5436_d8d331e35099ace0a79ef25226515a767410596022594182 |
| IPE | ISOPROPYL ETHER | 异丙醚 | 108-20-3 |  | pdf_6a8faacca882a39304796eef402a5436_46acac639b03886822af4c32f3b8001a7410596022594182 |
| IPH | ISOPHORONE | 异佛尔酮 | 78-59-1 | 3,5,5-Trimethyl-2-cyclohexane-1-one | pdf_6a8faacca882a39304796eef402a5436_c648afc6812c28eea45b199490d374817410596022594182 |
| IPI | ISOPHORONE DIAMINElPI | 异佛尔酮二胺 |  | 3-Aminomethyl-3,5,5-3-Aminomethyl-3,5,5-3-Aminomethyl-3,5,5-3-Aminomethyl-3,5,5- | pdf_6a8faacca882a39304796eef402a5436_39935c53da988ff58f4d3d61b71b0a027410596022594182 |
| IPL | ISOPHTHALIC ACID | 间苯二甲酸 | 121-91-5 | Benzene-1,3-dicarboxylic acidm-Phthalic acid | pdf_6a8faacca882a39304796eef402a5436_59247ff169daae72f78729374aaad1807410596022594182 |
| IPM | ISOPROPYL MERCAPTAN | 异丙硫醇 | 75-33-2 | Propane-2-thiol2-Propanethiol | pdf_6a8faacca882a39304796eef402a5436_863c57fd9029eb162cf68af327d60cf87410596022594182 |
| IPP | ISOPROPYLAMINE | 异丙胺 | 75-31-0 | 2-AminopropaneMonoisopropylamineiso-Propylamine | pdf_6a8faacca882a39304796eef402a5436_f31408a8c906d8a668f50087b7421a967410596022594182 |
| IPR | ISOPRENE | 异戊二烯 | 78-79-5 | beta-Methylbiviny12-Methyl-1, 3-butadiene | pdf_6a8faacca882a39304796eef402a5436_c8a2ec1aa114188e07e440916c8107ac7410596022594182 |
| IPT | ISOPENTANE | 异戊烷 | 78-78-4 | 2-Methylbutane | pdf_6a8faacca882a39304796eef402a5436_6ce20f113af1f8d58757e5ff5dee22a17410596022594182 |
| IPX | ISOPROPYL CYCLOHEXANE | 异丙基环己烷 | 696-29-7 |  | pdf_6a8faacca882a39304796eef402a5436_fbd693d109fe657e5d622d70d8f648457410596022594182 |
| ISA | ISODECYL ALCOHOL | 异癸醇 | 25339-17-7 |  | pdf_6a8faacca882a39304796eef402a5436_db3acb962a064a48e9045fa06d79e7077410596022594182 |
| ISP | O-ISOPROPYL PHENOL | 邻异丙基苯酚 |  | 2-Isopropyl phenolProdx 131 | pdf_6a8faacca882a39304796eef402a5436_d162871d3adba1bf56ea731278fae11e7410596022594182 |
| IVA | ISOVALERALDEHYDE | 异戊醛 | 590-86-3 | IsovaleralIsovaleric aldehyde3-Methylbutanal3-Methyl/bulryraldehyde | pdf_6a8faacca882a39304796eef402a5436_c114a43b552032900952d44abdf6cbe47410596022594182 |
| JPF | JET FUELS: JP-4 | 喷气燃料 JP-4 |  |  | pdf_6a8faacca882a39304796eef402a5436_c58a5c368bdfe29e98608c5837ffda937410596022594182 |
| JPO | JET FUELS: JP-1 | 喷气燃料 JP-1 |  | Fuel oil no. 1KeroseneKerosineRange oil | pdf_6a8faacca882a39304796eef402a5436_6982e961179aa7c16734bd9bdb48dfcd7410596022594182 |
| JPT | JET FUELS: JP-3 | 喷气燃料 JP-3 |  |  | pdf_6a8faacca882a39304796eef402a5436_ceaf10cf986b87f53913f9bba1fc0d1b7410596022594182 |
| JPV | JET FUELS: JP-5 | 喷气燃料 JP-5 |  | Kerosene, heavy | pdf_6a8faacca882a39304796eef402a5436_54082204f02c5edf35554c7613cce8b57410596022594182 |
| KPE | KEPONE | 十氯酮（开蓬） | 143-50-0 | ChlordeconeDecachloroketoneENT-16391GC-1189Merex | pdf_6a8faacca882a39304796eef402a5436_23b3a19e8e4f78f645ebbb4d7c0653667410596022594182 |
| KRS | KEROSENE | 煤油 |  | Fuel oil no. 1Illurating oilJet fuel: JP-1KerosineRange oil | pdf_6a8faacca882a39304796eef402a5436_1fd385c8b8afeddd69a67e04a01b29677410596022594182 |
| LAC | LEAD ACETATE | 乙酸铅 |  |  | pdf_6a8faacca882a39304796eef402a5436_34fc670071b76016174db0534d12034f7410596022594182 |
| LAH | LITHIUM ALUMINUM HYDRIDE | 氢化铝锂 | 16853-85-3 |  | pdf_6a8faacca882a39304796eef402a5436_49488554441ea9138e524384a51748c17410596022594182 |
| LAL | LINEAR ALCOHOLS | 直链醇 |  |  | pdf_6a8faacca882a39304796eef402a5436_87bf77aa1b4c4205ee8bc0cdad8a3e3c7410596022594182 |
| LAR | LEAD ARSENATE | 砷酸铅 | 7784-40-9 | Lead arsenate, acidPlumbous arsenate | pdf_6a8faacca882a39304796eef402a5436_b769b620d3bf9ec6f73f1e1f296ba9a87410596022594182 |
| LBC | LITHIUM BICHROMATE | 重铬酸锂 |  | Lithium bichromate dilydrateLithium dichromate | pdf_6a8faacca882a39304796eef402a5436_c34843c2745d2f76c6bdc28c6f3511a07410596022594182 |
| LCL | LEAD CHLORIDE | 氯化铅 | 7758-95-4 | Lead (II) chlorideLead dichloridePlumbous chloride | pdf_6a8faacca882a39304796eef402a5436_f64286fd6fe5d61089a4947fbfe782c67410596022594182 |
| LCR | LITHIUM CHROMATE | 铬酸锂 | 14307-35-8 | Chromic solid, lithium saltChromium lithium oxideDilithium chromate | pdf_6a8faacca882a39304796eef402a5436_106f7a9d83ab3e629011a75c17e5253b7410596022594182 |
| LFB | LEAD FLUOROBORATE | 氟硼酸铅 | 13814-96-5 | Lead fluoroborateLead fluoroborate solution | pdf_6a8faacca882a39304796eef402a5436_fd5b8c0854114e0a49424df59975f8a57410596022594182 |
| LFR | LEAD FLUORIDE | 氟化铅 | 7783-46-2 | Lead fluoridePlumbous fluoride | pdf_6a8faacca882a39304796eef402a5436_4cdfe4ea3730a6bd26066553bfd6d2527410596022594182 |
| LHD | LITHIUM HYDRIDE | 氢化锂 | 7580-67-8 |  | pdf_6a8faacca882a39304796eef402a5436_1a368443369076b22d032ffe930e97ea7410596022594182 |
| LID | LEAD IODIDE | 碘化铅 | 13779-98-1 |  | pdf_6a8faacca882a39304796eef402a5436_7d412160d181bac49d74fea2d72647b27410596022594182 |
| LLS | LATEX, LIQUID SYNTHETIC | 合成胶乳（液体） |  | Plastic latexSynthetic rubber latex | pdf_6a8faacca882a39304796eef402a5436_43aca2467b8a2d359144f5c1d46806a47410596022594182 |
| LNG | LIQUEFIED NATURAL GAS | 液化天然气（LNG） |  |  | pdf_6a8faacca882a39304796eef402a5436_bef2fcb49a45b81258049ec2415c28d57410596022594182 |
| LNI | LACTONITRILE SOLUTION (80% OR LESS) | 乳腈溶液（≤80%） | 78-97-7 | Acetocyyanhydrin2-Hydroxypropionitrile | pdf_6a8faacca882a39304796eef402a5436_91caca031d940181f0f481d02e1b9ad87410596022594182 |
| LNT | LEAD NITRATE | 硝酸铅 | 10099-74-8 | Nitric acid, lead ll salt | pdf_6a8faacca882a39304796eef402a5436_1faf75dd1bab65b82d3d6aa1ba3e7bdd7410596022594182 |
| LPG | LIQUEFIED PETROLEUM GAS | 液化石油气（LPG） |  | Bottled gasLPGPropane-butane-(propylene)Pyrofax | pdf_6a8faacca882a39304796eef402a5436_f1a45a239f0bb397d300d5334e2808c17410596022594182 |
| LPO | LAUROYL PEROXIDE | 过氧化月桂酰 | 105-74-8 | Dilauroyl peroxideDodecanoyl peroxide | pdf_6a8faacca882a39304796eef402a5436_2977ad703de8913b70bb82fb662d1cf87410596022594182 |
| LRA | LAURIC ACID | 月桂酸 | 143-07-7 |  | pdf_6a8faacca882a39304796eef402a5436_09d52c7efa5f51108ea34b4c33e015a07410596022594182 |
| LRM | LAURYL MERCAPTAN | 月桂硫醇 | 112-55-0 | 1-Dodecanethroidodecyl mercaptan | pdf_6a8faacca882a39304796eef402a5436_3190893ba8da1603fd98c829551d245c7410596022594182 |
| LSA | LEAD STEARATE | 硬脂酸铅 | 1072-35-1 | Neutral lead starateStearic acid, lead salt | pdf_6a8faacca882a39304796eef402a5436_1951356424677825399a42d1a75307ba7410596022594182 |
| LSF | LEAD SULFATE | 硫酸铅 | 7446-14-2 |  | pdf_6a8faacca882a39304796eef402a5436_4ffb630cfa3451288ea90e5d08d79c7c7410596022594182 |
| LSU | LEAD SULFIDE | 硫化铅 | 12179-39-4 | Galera Plumbous sulfide | pdf_6a8faacca882a39304796eef402a5436_536037415ecf573a4088a5a675498e3b7410596022594182 |
| LTA | LACTIC ACID | 乳酸 | 50-21-5 | 2-Hydroxyproponic acidalpha-Hydroxyproponic acidMilk acidRacemic lactic acid | pdf_6a8faacca882a39304796eef402a5436_768163e0999fd394fe07d7f5206fa88b7410596022594182 |
| LTC | LEAD THIOCYANATE | 硫氰酸铅 | 592-87-0 | Lead suffocyanate | pdf_6a8faacca882a39304796eef402a5436_939f3c64706aa516c2f2d7f035f5b8a47410596022594182 |
| LTH | LITHARGE | 氧化铅（密陀僧） |  | Lead monoxideLead oxide yellowLead protoxideMassicotPlumbous oxide | pdf_6a8faacca882a39304796eef402a5436_5dc1dc1555b46022e161148271878b3e7410596022594182 |
| LTM | LITHIUM | 锂 | 7439-93-2 |  | pdf_6a8faacca882a39304796eef402a5436_d51c7bf364cef5e75a4ebc1660066a237410596022594182 |
| LTS | LEAD THIOSULFATE | 硫代硫酸铅 | 13478-50-7 | Lead hyposulifteThiosulfuric acid, lead salt | pdf_6a8faacca882a39304796eef402a5436_bdff858e53aba07a64bab7499f01c0717410596022594182 |
| LTT | LEAD TETRAACETATE | 四乙酸铅 | 546-67-8 | Lead IV acetate | pdf_6a8faacca882a39304796eef402a5436_f1581246ca9dd9f0e03505d70c5c64e07410596022594182 |
| LTU | LEAD TUNGSTATE | 钨酸铅 | 7759-01-5 | Lead wollramateRaspiteScheelteStolzite | pdf_6a8faacca882a39304796eef402a5436_8866bd629cc35387ccd75eeabb572d667410596022594182 |
| MAA | METHYL AMYL ALCOHOL | 甲基戊醇 | 108-11-2 |  | pdf_6a8faacca882a39304796eef402a5436_25cbca9b626a39c405e97d559a64da767410596022594182 |
| MAC | METHYL AMYL ACETATE | 乙酸甲基戊酯 | 108-84-9 |  | pdf_6a8faacca882a39304796eef402a5436_0921766c75be6c756343e85893c1aece7410596022594182 |
| MAD | METHACRYLIC ACID | 甲基丙烯酸 | 79-41-4 | 2-Methylacrylic acidalpha-Methylacrylic acid2-Methylpropenic acidPropenionic aci | pdf_6a8faacca882a39304796eef402a5436_8109d8dfbf9b4d09d28becee6af0675e7410596022594182 |
| MAE | METHYL ACETOACETATE | 乙酰乙酸甲酯 | 105-45-3 | Acetoacetic acid, methyl esterButanolic acid, 3-oxo-methylester (9ci)Methyl acet | pdf_6a8faacca882a39304796eef402a5436_415fdc321ba440ed8f2cee83e3115b107410596022594182 |
| MAL | METHYL ALCOHOL | 甲醇 | 67-56-1 |  | pdf_6a8faacca882a39304796eef402a5436_1f61733c0e48a49fd83d018c1b8b59967410596022594182 |
| MAM | METHYL ACRYLATE | 丙烯酸甲酯 | 96-33-3 | Acrylic acid, methyl esterMethyl 2-propenoate | pdf_6a8faacca882a39304796eef402a5436_13b1bbe92e4e6b8681a54758c722fbad7410596022594182 |
| MAN | N-METHYLANILINE | N-甲基苯胺 | 100-61-8 |  | pdf_6a8faacca882a39304796eef402a5436_c3044b21777aa62ea4d40ae1d7e1231e7410596022594182 |
| MAP | METHYL ACETYLENE, PROPADIENE MIXTURE | 甲基乙炔/丙二烯混合物（MAPP气） |  | Allene-methylacetylene mixtureMAPP gasMethylacylene-alene mixturePropadiene-meth | pdf_6a8faacca882a39304796eef402a5436_0c9269be09a07c13e41b69203e131a747410596022594182 |
| MAT | MERCURIC ACETATE | 乙酸汞 | 1600-27-7 |  | pdf_6a8faacca882a39304796eef402a5436_12a26ca0e6bc826682d240aa68fd31277410596022594182 |
| MBA | A-METHYLBENZYL ALCOHOL | α-甲基苄醇 |  | alpha-Methyl benzene methanolMethylphenyl methanol1-Phenylethanola-Phenyl ethyl  | pdf_6a8faacca882a39304796eef402a5436_4086e8b2c417e612249d75c89198a1ec7410596022594182 |
| MBE | METHYL TERT-BUTYL ETHER | 甲基叔丁基醚（MTBE） | 1634-04-4 | tert-Butyl methyl ether2-Methoxy-2-methyl propane2-Methyl-2-methoxy propane | pdf_6a8faacca882a39304796eef402a5436_660183913b3700759a62526c4f8b422c7410596022594182 |
| MBK | METHYL N-BUTYL KETONE | 甲基正丁基酮 | 591-78-6 | n-Butyl methyl ketone2-Hexanone | pdf_6a8faacca882a39304796eef402a5436_5473381ceab6e893b2e85e2522d42e217410596022594182 |
| MBL | METHYL BUTENOL | 甲基丁烯醇 |  | 1-Buten-3-ol, 3-methyl-3-buten-2-ol3-Methyl-1-buten-3-ol3-Methyl-buten-(1)-ol(3) | pdf_6a8faacca882a39304796eef402a5436_7d4d0ab5c9f9c960f00a907f56743df97410596022594182 |
| MBO | 3-METHYL-2-BUTANONE | 3-甲基-2-丁酮 | 563-80-4 |  | pdf_6a8faacca882a39304796eef402a5436_85b3f65b55463ae075bf01536d7492827410596022594182 |
| MBU | METHYL BUTYRATE | 丁酸甲酯 | 623-42-7 | Butanoic acid, methyl esterButyric-n-methyl esterMethyl-n-butanoateMethyl-n-buty | pdf_6a8faacca882a39304796eef402a5436_0304cd9845d6de47e0bd384fd7c2ca177410596022594182 |
| MBY | METHYL BUTYNOL | 甲基丁炔醇 |  | 2-Hydroxy-2-methyl-3-butyne2-Methyl-3-butyn-2-ol | pdf_6a8faacca882a39304796eef402a5436_c29b4fb2f7921995870c78894487d8467410596022594182 |
| MBZ | METHYL BENZOATE | 苯甲酸甲酯 | 93-58-3 | Benzic acid, methyl esterEssence of NiobeMethyl benzenecarboxylateNobe oilOil of | pdf_6a8faacca882a39304796eef402a5436_fe5b8c6721fe2c89a58e76b99b2245157410596022594182 |
| MCA | CHOROACETIC ACID | 氯乙酸 | 79-11-8 | Choracetic acidMonochloracetic acid | pdf_6a8faacca882a39304796eef402a5436_607b967a1d902b83a8f73bd1cd480f127410596022594182 |
| MCC | MERCURIC AMMONIUM CHLORIDE | 氯化汞铵 |  |  | pdf_6a8faacca882a39304796eef402a5436_5aad7fa910148512fe28eb9073036c847410596022594182 |
| MCD | MERCAPTODIMETHUR | 灭虫威 | 2032-65-7 | Bay 37344 Mesurol Methicarb Methercapturon | pdf_6a8faacca882a39304796eef402a5436_ebcd5fb0f1d4c2d55849e199020bbdf87410596022594182 |
| MCF | CHORODIFLUOROMETHANE | 氯二氟甲烷 | 75-45-6 |  | pdf_6a8faacca882a39304796eef402a5436_eaedbe0835b16bfd650950f8c140c18c7410596022594182 |
| MCK | METHYLCYCLOPENTADIENE DIMER | 甲基环戊二烯二聚体 | 26472-00-4 | 4.7-Methanoïndene, 3a,4,7,7a-tetrahydrodimethylBis(methyl-cyclopentadiene)3a,4,7 | pdf_6a8faacca882a39304796eef402a5436_e9064d1f1d4dd59012f3cc5ecd3e7ce67410596022594182 |
| MCL | METHALLYL CHLORIDE | 甲代烯丙基氯 | 563-47-3 |  | pdf_6a8faacca882a39304796eef402a5436_1f990ec978d27b0e5b55a4a1df1da9ae7410596022594182 |
| MCM | MONOCHLOROTRIFLUOROMETHANE | 一氯三氟甲烷 | 75-72-9 | ChlorotrifluomethaneF-13Freon 13TrifluorchloromethaneTrifluorethyl chloride | pdf_6a8faacca882a39304796eef402a5436_20dfd9dd95bf76c46f1f00d35f731b617410596022594182 |
| MCN | MERCURIC CYANIDE | 氰化汞 | 592-04-1 | CianurinaMercury cyanideMercury (I) cyanide | pdf_6a8faacca882a39304796eef402a5436_f83ac8305be66401a3aad2d4589c31f17410596022594182 |
| MCO | METOLACHLOR | 异丙甲草胺 | 51218-45-2 | CGA24705CodaColoran multiDualMetellachlorMilocepOntrack 86PrimagranPrimextra | pdf_6a8faacca882a39304796eef402a5436_51cd784533f76f2ee7e30a9d158370147410596022594182 |
| MCP | METHYL CYCLOPENTANE | 甲基环戊烷 | 96-37-7 | Cyclopentane, methyl | pdf_6a8faacca882a39304796eef402a5436_3e62d0d43aa27e4cd2523f3b2c3317807410596022594182 |
| MCR | MERCURY | 汞 | 7439-97-6 | Quicksilver | pdf_6a8faacca882a39304796eef402a5436_519ae2e5a86fe4ca2b2d9dcc0e2215e37410596022594182 |
| MCS | METHYLDICHLOROSILANE | 甲基二氯硅烷 | 75-54-7 |  | pdf_6a8faacca882a39304796eef402a5436_e1670ca26e255342e66448ebefc8ed5e7410596022594182 |
| MCT | METHYLCYCLOPENTADIENYLMANGANESE TRICARBONYL | 甲基环戊二烯三羰基锰（MMT） |  | Combustion improper C-12 | pdf_6a8faacca882a39304796eef402a5436_a37482437831d83bddbf3908468c54e27410596022594182 |
| MCX | O-METHYLCYCLOHEXANONE | 邻甲基环己酮 | 583-60-8 | 2-Methylcyclohexanone | pdf_6a8faacca882a39304796eef402a5436_1a1c02cd4a82010f13da25085040f08d7410596022594182 |
| MCY | METHYLCYCLOHEXANE | 甲基环己烷 | 108-87-2 | CyclohexylmethaneHexahydrotoluensextone BToluene, hexahydroun 2299 (DOT) | pdf_6a8faacca882a39304796eef402a5436_797005487b6f6922209b7b6533af5e8a7410596022594182 |
| MDC | METHYL DICHLOROACETATE | 二氯乙酸甲酯 | 116-54-1 | Dichloroacetic acid, methylesterMethyl dichloroethanoate | pdf_6a8faacca882a39304796eef402a5436_fd9423d9e16ee23b21a797a11121e8347410596022594182 |
| MDE | METHYL DIETHANOLAMINE | 甲基二乙醇胺 | 105-59-9 | MAEA2.2-Methyliminodiethanol | pdf_6a8faacca882a39304796eef402a5436_3bc531520f7e14375ca3777a27f5ae0f7410596022594182 |
| MEA | MONOETHANOLAMINE | 单乙醇胺 | 141-43-5 | 2-Aminoethanolbeta-Aminoethyl alcoholEthanolamine2-Hydroxythylamine | pdf_6a8faacca882a39304796eef402a5436_89e6581fb955217b3231c47e6f1df9a67410596022594182 |
| MED | METHYL CHLOROACETATE | 氯乙酸甲酯 | 96-34-4 |  | pdf_6a8faacca882a39304796eef402a5436_b9943457d0b53e81c6de7ceefa30373f7410596022594182 |
| MEK | METHYL ETHYL KETONE | 甲乙酮（丁酮） | 78-93-3 | 2-ButanoneEthyl methyl ketoneMEK | pdf_6a8faacca882a39304796eef402a5436_3ff8c048e30b530e2fc57ba32c6f39af7410596022594182 |
| MEN | 2-METHYL-6-ETHYL ANILINE | 2-甲基-6-乙基苯胺 | 24549-06-2 | 6-Ethyl-2-methyl-line6-Ethyl-o-toluidine2-Methyl-6-ethylbenzeneamine | pdf_6a8faacca882a39304796eef402a5436_9ac30a2b08faefd7877461b2df2b3c787410596022594182 |
| MEP | METHYLETHYLPYRIDINE | 甲乙基吡啶 | 104-90-5 | Aldehyde-colidineAldehydine5-Ethyl-2-methyl pyridine5-Ethyl-2-picolineMEP | pdf_6a8faacca882a39304796eef402a5436_8956ab124d1ff82cb39f180a3d5c91737410596022594182 |
| MES | METHYL SALICYLATE | 水杨酸甲酯 | 119-36-8 | o-Anisic acidBenzoic acid, 2-methoxy-Betula or gaultheria oilo-Alethoxybenzic ac | pdf_6a8faacca882a39304796eef402a5436_0aab7aede75dfe114fbc317960f89bdf7410596022594182 |
| MET | METHACRYLONITRILE | 甲基丙烯腈 | 126-98-7 |  | pdf_6a8faacca882a39304796eef402a5436_7f2052553e167231192dcf083e7fd42d7410596022594182 |
| MFA | LEAD ALKYLS | 烷基铅 |  |  | pdf_6a8faacca882a39304796eef402a5436_670cf9ae2f35b8db1dabee43e36e120a7410596022594182 |
| MFM | METHYL FORMATE | 甲酸甲酯 | 107-31-3 | Formic acid, methyl ester | pdf_6a8faacca882a39304796eef402a5436_a28a70caab8af6728a6a2385c966191b7410596022594182 |
| MGN | MAGNESIUM NITRATE | 硝酸镁 | 10377-60-3 | Magnesium nitrate hexahydrateNitromagnesite | pdf_6a8faacca882a39304796eef402a5436_140acb120e778f7066d17c9188db23257410596022594182 |
| MGX | MAGNESIUM | 镁 | 7439-95-4 | Magnesium perchlorate | pdf_6a8faacca882a39304796eef402a5436_8726ad5bb831ccb6d936b840da86d1527410596022594182 |
| MHB | 2-METHYL-2-HYDROXY-3-BUTYNE | 2-甲基-2-羟基-3-丁炔 | 115-19-5 | DimethylacelylenecarbinalDimethylethynylcarbinol1.1-Dimethypropyl alcoholMethyl  | pdf_6a8faacca882a39304796eef402a5436_e66058dcbf709abefbafa85d89fac2897410596022594182 |
| MHC | METHYL CHLOROFORMATE | 氯甲酸甲酯 | 79-22-1 | Chiorocarbonic acid, methyl esterChloroformic acid, methyl esterMethyl chlorocar | pdf_6a8faacca882a39304796eef402a5436_33ce603d7f82843279f72c137513c8ea7410596022594182 |
| MHK | METHYL HEPTYL KETONE | 甲基庚基酮 | 821-55-6 |  | pdf_6a8faacca882a39304796eef402a5436_f4db2f86ebe48f69924b2e6c794db2787410596022594182 |
| MHX | 2-METHYLCYCLOHEXA | 2-甲基环己醇 |  | Hexahydrorescols | pdf_6a8faacca882a39304796eef402a5436_d2b4203069a928b5e51d137d055703867410596022594182 |
| MHZ | METHYLHYDRAZINE | 甲基肼 | 60-34-4 | MMHMonomethylhydrazine | pdf_6a8faacca882a39304796eef402a5436_c4be2a6454f3a8209b2145b95b8d1e147410596022594182 |
| MIC | METHYL ISOBUTYL CARBINOL | 甲基异丁基甲醇 | 108-11-2 | Isobulty/methyl/carbinolMAAMOHMethyl amyl alcohol4-Methyl-2-pentanolMIBCMIC | pdf_6a8faacca882a39304796eef402a5436_bb038da1070056dbb7e21a5ae9db59297410596022594182 |
| MID | MERCURIC IODIDE | 碘化汞 | 7774-29-0 | Mercuric iodide, redMercury biodide | pdf_6a8faacca882a39304796eef402a5436_74b4f32c0eaa6bc1a1847010c1afbfd47410596022594182 |
| MIK | METHYL ISOBUTYL KETONE | 甲基异丁基酮（MIBK） | 108-10-1 |  | pdf_6a8faacca882a39304796eef402a5436_d24bb1b43755f2ebf159aa0b25dcbc557410596022594182 |
| MIO | METHYL IODIDE | 碘甲烷 | 74-88-4 | IodomethaneMonoiodomethane | pdf_6a8faacca882a39304796eef402a5436_b3ee57b5a175f2fe6c66fadbdec6217f7410596022594182 |
| MIS | METHYL ISOCYANATE | 异氰酸甲酯 | 624-83-9 | IsocyanatomethaneIsocyanic acid, methyl esterMethane, isocyanato-Methyl carbonim | pdf_6a8faacca882a39304796eef402a5436_8109eec57ca0c07c8b59293a0ae8ed297410596022594182 |
| MIT | METHYL ISOTHIOCYANATE | 异硫氰酸甲酯 | 556-61-6 | IsothicyanatomethineIsothicyanatic acid, methyl esterMethyl mustard oil | pdf_6a8faacca882a39304796eef402a5436_be0d9c7ce4492db7054893401335a7527410596022594182 |
| MKE | METHYL PROPYL KETONE | 甲基丙基酮 | 107-87-9 | 2-Pentanone | pdf_6a8faacca882a39304796eef402a5436_4f623c4b2b75882f6c3388b95fde47cc7410596022594182 |
| MLA | MALEIC ANHYDRIDE | 顺丁烯二酸酐（马来酸酐） | 108-31-6 | cis-Butenedioic anhydride2.5-FuranedionetoXolic anhydride | pdf_6a8faacca882a39304796eef402a5436_ebc8e34b66a1d5460e4ba222fba371f77410596022594182 |
| MLH | MALEIC HYDRAZ | 马来酰肼 |  | 1.2-Dihydro-3.6-pyridazinedone6-Hydroxy-(2h)-pyridazinoneMalazideMaleic acid hyd | pdf_6a8faacca882a39304796eef402a5436_22a5cfe438ac06ec53511472fa25075d7410596022594182 |
| MLI | MALEIC ACID | 顺丁烯二酸（马来酸） | 110-16-7 | cis-Butenedioic acidcis-1,2-EthylenedicarboxylicacidMaleinic acidMalenic acidTox | pdf_6a8faacca882a39304796eef402a5436_435cd8711bec10b1f592faffe3f988887410596022594182 |
| MLL | METHYL ALLYL ALCOHOL | 甲基烯丙醇 |  | 2-4-2ly-2-propen-1-ol | pdf_6a8faacca882a39304796eef402a5436_a6cc5e99096c409cb4614c5114ece8807410596022594182 |
| MLP | 3-METHYLPYRIDINE | 3-甲基吡啶 | 108-99-6 | 3-Picolineb-Picolinem-PicolinePyridine, 3-methylUN 2313 (DOT) | pdf_6a8faacca882a39304796eef402a5436_e25a8446c765cfecb278b9f4f9cb95d47410596022594182 |
| MLT | MALATHION | 马拉硫磷 | 121-75-5 | Cythinfection | pdf_6a8faacca882a39304796eef402a5436_a87b47bf1eccc708980fb0ef4e10c95a7410596022594182 |
| MMC | METHYL MERCAPTAN | 甲硫醇 | 74-93-1 | MercapotmethaneMethaneethiolMethyl sulhydrateThiomethyl alcohol | pdf_6a8faacca882a39304796eef402a5436_9cdc3197da06f396dc7e4d2605e765c47410596022594182 |
| MME | MONOMETHYL ETHANOLAMINE | 单甲基乙醇胺 |  | 2-(Methylamino)ethanolN-Methyl ethanolamine | pdf_6a8faacca882a39304796eef402a5436_1d02bb893d1b744994d4c9e456c64c157410596022594182 |
| MMM | METHYL METHACRYLATE | 甲基丙烯酸甲酯（MMA） | 80-62-6 | Methacrylate monomer Methacrylic acid, methyl este Methyl a-methylacrylate Methy | pdf_6a8faacca882a39304796eef402a5436_647bfe247bd0633a9f9438c652e3030f7410596022594182 |
| MNA | 1-METHYLNAPHTHALENE | 1-甲基萘 | 90-12-0 | alpha-Methylnaphthalene | pdf_6a8faacca882a39304796eef402a5436_d1af3011c5171dce20b0ce3e982459707410596022594182 |
| MNS | MINERAL SPIRITS | 矿物油精 |  | NaphthaPetroleum spirits | pdf_6a8faacca882a39304796eef402a5436_67455941595c29865b32a51c4724b7c57410596022594182 |
| MNT | MERCURIC NITR | 硝酸汞 |  | Mercury (II) nitrateMercury nitrate monohydrateMercury peritrate | pdf_6a8faacca882a39304796eef402a5436_1d5afc2e9c35aaa04bb62968cdc737877410596022594182 |
| MOA | 3-METHOXYBUTYL ACETATE | 3-甲氧基丁基乙酸酯 | 4435-53-4 | Acetic acid, 3-methoxybutylester1-Butanol, 3-methoxyacetateButoxylMethyl-1,3-but | pdf_6a8faacca882a39304796eef402a5436_edcc1c0cc8f1cdcbf108c9e9967710ef7410596022594182 |
| MOC | METHOXYCHLOR | 甲氧滴滴涕 | 72-43-5 |  | pdf_6a8faacca882a39304796eef402a5436_cf1bcad7c0cf657f4840071a70bfac957410596022594182 |
| MOX | MERCURIC OXIDE | 氧化汞 | 21908-53-2 | Mercuric oxide, redMercuric oxide, yellowMercuric oxide | pdf_6a8faacca882a39304796eef402a5436_1f9cbb173d6c88074b26de11021547167410596022594182 |
| MPA | MONOISOPROPANOLAMINE | 单异丙醇胺 | 78-96-6 | 1-Amino-2-propanol2-HydroxypropylamineIsopropanolamine | pdf_6a8faacca882a39304796eef402a5436_8b4326ace388a6b384050ef0c65350177410596022594182 |
| MPC | MAGNESIUM PERCHLORATE | 高氯酸镁 | 10034-81-8 |  | pdf_6a8faacca882a39304796eef402a5436_bc5a64edec0fa823eb205839177b95d67410596022594182 |
| MPD | METHYL PHOSPHONOTHIOIC DICHLORIDE | 甲基硫代膦酰二氯 | 676-98-2 | MPTD | pdf_6a8faacca882a39304796eef402a5436_5676a6172c9a78dfafdbfe350baee2997410596022594182 |
| MPE | 2-METHYL-1-PENTENE | 2-甲基-1-戊烯 | 763-29-1 |  | pdf_6a8faacca882a39304796eef402a5436_08bd8cadfe14f14b7c00b4e7718bb6f47410596022594182 |
| MPF | 4-METHYLPYRIDINE | 4-甲基吡啶 | 108-89-4 | 4-Picoline gamma-Picoline p-Picoline UN 2313 (DOT) | pdf_6a8faacca882a39304796eef402a5436_5ab854d552b5230ec514ce72eb4cb88d7410596022594182 |
| MPK | METHYL ISOPROPENYL KETONE | 甲基异丙烯基酮 | 814-78-8 | Isopropyl/methyl ketone2-Methyl-1-butene-3-one | pdf_6a8faacca882a39304796eef402a5436_3f767c0f08e3da7b7987e27e050445e27410596022594182 |
| MPL | MORPHOLINE | 吗啉 | 110-91-8 | Diethyleneimide oxideDiethylene imidoxideDiethylene oximideTetrahydro-2h-1, 4-ox | pdf_6a8faacca882a39304796eef402a5436_e0bf9c352281ae965fb50848706c1a8a7410596022594182 |
| MPR | 2-METHYLPYRIDINE | 2-甲基吡啶 | 109-06-8 | alpha-Methylpyridine Picoline 2-Picoline alpha-Picoline | pdf_6a8faacca882a39304796eef402a5436_935c69d8d11328fd6275c43694b47c017410596022594182 |
| MPT | METHYL PARATHION | 甲基对硫磷 | 298-00-0 |  | pdf_6a8faacca882a39304796eef402a5436_135055502b06284bbf530b3d54877a3b7410596022594182 |
| MPY | 1-METHYLPYRROLID | 1-甲基吡咯烷酮 |  | 1-Methyl-2-pyrolidinoneN-MethylpyyrolidoneN-Methyl-alpha-pyrolidone | pdf_6a8faacca882a39304796eef402a5436_230661ab64a0f91737e311db64a6c95a7410596022594182 |
| MRC | MERCURIC CHLORIDE | 氯化汞（升汞） | 7487-94-7 |  | pdf_6a8faacca882a39304796eef402a5436_467eb608edc6e9d88497d0452ef222b67410596022594182 |
| MRE | MYRCENE | 月桂烯 | 123-35-3 | 3-Methylene-7-methyl 1.6-octadiene2-Methyl-6-methylene-2,7-octadiene1,6-Octadien | pdf_6a8faacca882a39304796eef402a5436_e81ef1da0bba4250f46034878202b6c77410596022594182 |
| MRN | MERCUROUS NITRATE | 硝酸亚汞 | 10415-75-5 | Mercurous nitrate monohydrateMercury protonitrate | pdf_6a8faacca882a39304796eef402a5436_de7da7c1899cefd8df1245d94ca2bcbe7410596022594182 |
| MRR | MERCUROUS CHLORIDE | 氯化亚汞（甘汞） |  | CalomelMercury monochlorideMercury protochlorideMercury subchlorideMid mercury c | pdf_6a8faacca882a39304796eef402a5436_3fc136e5cfc6faeec71f5b23626bbf187410596022594182 |
| MRS | MERCURIC SULFATE | 硫酸汞 | 7783-35-9 |  | pdf_6a8faacca882a39304796eef402a5436_840b5653fd2d49e2f007e0db00b3562b7410596022594182 |
| MRT | MERCURIC THIOCYANATE | 硫氰酸汞 | 592-85-8 | Mercuric sulfoyanateMercuric sulfoyanadeMercury rhodande | pdf_6a8faacca882a39304796eef402a5436_55a0a86b79ec8a8b900abd664b1d68677410596022594182 |
| MRX | MIREX | 灭蚁灵 | 2385-85-5 |  | pdf_6a8faacca882a39304796eef402a5436_8f91cf9e29c4c1e120da610add744ead7410596022594182 |
| MSA | METHANEARSONIC ACID, SODIUM SALT | 甲基胂酸钠 | 22969-24-0 | Diodulum methane arsonateDisodium methyl arsonateDSMAMonosodium methane arsonate | pdf_6a8faacca882a39304796eef402a5436_1ebaa1f30795f400326c1912ef89ac7c7410596022594182 |
| MSF | MERCURIC SULFIDE | 硫化汞 | 37251-50-6 |  | pdf_6a8faacca882a39304796eef402a5436_5b3fc523c8bd5ae6cdcd10173386efd37410596022594182 |
| MSO | MESITYL OXIDE | 异丙叉丙酮 | 141-79-7 | IsopropylideneacetoneMethyl isobutlenyl ketone4-Methyl-3-pentene-2-one | pdf_6a8faacca882a39304796eef402a5436_5d43f13719f22ef0ff29581766cb92c17410596022594182 |
| MSR | ALPHA-METHYLSTYRENE | α-甲基苯乙烯 | 98-83-9 | Isopropylbenzene1-Methyl-1-phenylethylenePheny/propylene | pdf_6a8faacca882a39304796eef402a5436_d900adf0791fb51aae475daf33bf057a7410596022594182 |
| MSZ | METHYLAMINE SOLUTION | 甲胺溶液 | 74-89-5 |  | pdf_6a8faacca882a39304796eef402a5436_a13af8e90265cd6681d8cb09abd922587410596022594182 |
| MTA | METHYLAMINE | 甲胺 | 74-89-5 |  | pdf_6a8faacca882a39304796eef402a5436_782c8616d8b51b27a40c266e7595c4c27410596022594182 |
| MTB | METHYL BROMIDE | 溴甲烷 | 74-83-9 | Bromomethane Embafume M-B-C fumant Monobromomethane | pdf_6a8faacca882a39304796eef402a5436_67dd1bc50b9909a6701fab019b71052a7410596022594182 |
| MTC | METHYL CHLORIDE | 氯甲烷 | 74-87-3 |  | pdf_6a8faacca882a39304796eef402a5436_debe24425a640a06f6e18f8a85e601377410596022594182 |
| MTE | MONOCHLOROTETRAFLUOROETHANE | 一氯四氟乙烷 | 354-25-6 |  | pdf_6a8faacca882a39304796eef402a5436_297ced10090adcaf8a642883fc164bdc7410596022594182 |
| MTF | METHYL FORMAL | 甲缩醛 |  | DimethoxymethaneDimethyl formalFormaldehyde dimethylacetolMethylalMethylene dime | pdf_6a8faacca882a39304796eef402a5436_54d24b00688e52d1e6ae352ca72540877410596022594182 |
| MTH | METH | 甲烷 | 537-46-2 | Marsh gasNatural gas | pdf_6a8faacca882a39304796eef402a5436_3ac3567258991d7d82a4087cab4006667410596022594182 |
| MTN | 4-METHYL-1-PENTENE | 4-甲基-1-戊烯 | 691-37-2 |  | pdf_6a8faacca882a39304796eef402a5436_d7b4390cbcde52512ad6b2cdd14a49ca7410596022594182 |
| MTO | MOLYBDIC TRIOXIDE | 三氧化钼 | 1313-27-5 | Molybdenum trioxideMolybdic anthyride | pdf_6a8faacca882a39304796eef402a5436_9c4ba86e020b43e60ade2e2d5f2b33dd7410596022594182 |
| MTS | METHYLTRICHLOROSILANE | 甲基三氯硅烷 | 75-79-6 | Trichloromethylsilane | pdf_6a8faacca882a39304796eef402a5436_6f176226a48aecbd6b8ea6b141c216697410596022594182 |
| MTT | METHYL ACETATE | 乙酸甲酯 | 79-20-9 | Acetic acid, methyl ester | pdf_6a8faacca882a39304796eef402a5436_8fbcd39a941b30ae96c94b266af0d9b97410596022594182 |
| MVK | METHYL VINYL KETONE | 甲基乙烯基酮 | 78-94-4 | 3-Buten-2-one | pdf_6a8faacca882a39304796eef402a5436_559e95180af701dc8d2ceeda814bced57410596022594182 |
| NAA | NITRILOTRIACETIC ACID AND SALTS | 氮川三乙酸及其盐 |  | Disodium nitriotriacetateNTATrigtycineTrisodium nitriotriacetate | pdf_6a8faacca882a39304796eef402a5436_1ca43055fee411a44cf249214f0595397410596022594182 |
| NAB | NABAM | 代森钠 | 142-59-6 | Chem bamDosdiumethylenebis [dithiocarbamate]DithaneEBDC, sodium saltEthylenebis  | pdf_6a8faacca882a39304796eef402a5436_713efe57213168803cc2642163f968557410596022594182 |
| NAC | NITRIC ACID | 硝酸 | 7697-37-2 |  | pdf_6a8faacca882a39304796eef402a5436_a79c4f1f2a3daa0b653c0e4dbfa1710a7410596022594182 |
| NAE | NONYL ACETATE | 乙酸壬酯 | 143-13-5 | Acetate C-9Acetic acid, n-nonyl esterNonanol acetaten-Nonyl acetate | pdf_6a8faacca882a39304796eef402a5436_f7acc58025b94eaf40cbea29a242a3fc7410596022594182 |
| NAL | 4-NITROANILINE | 4-硝基苯胺 | 100-01-6 | 1-Amino-4-nitrobenzeneAzoic diazo component 37Fast red GG baseFast red IG basep- | pdf_6a8faacca882a39304796eef402a5436_8a7cf7721a2b2bc7239ff15ba83344a67410596022594182 |
| NAN | NONANE | 壬烷 | 111-84-2 | n-Nonane | pdf_6a8faacca882a39304796eef402a5436_ea4fe778050a4b6488480a86e671cbb77410596022594182 |
| NAO | 1-NAPHTHYLAMINE | 1-萘胺 | 134-32-7 | 1-Aminonaphthalenealpha-Naphthylamne | pdf_6a8faacca882a39304796eef402a5436_1104601aced8d7f1d05bd563ff2e634e7410596022594182 |
| NAS | NICKEL AMMONIUM SULFATE | 硫酸镍铵 | 15699-18-0 | Ammonium disfilatonicelate (II)Ammonium nickel sulfateNickel ammonium sulfatehex | pdf_6a8faacca882a39304796eef402a5436_a37f20938744f625aa93cafb720eb8357410596022594182 |
| NBR | NICKEL BROMIDE | 溴化镍 |  | Nickel bromide trihydrate | pdf_6a8faacca882a39304796eef402a5436_d405b67e9ff639015c552d14241c56087410596022594182 |
| NCL | NICKEL CHLORIDE | 氯化镍 | 7718-54-9 | Nickel chloride hexahydrate | pdf_6a8faacca882a39304796eef402a5436_241e8ce5eccc5cf12db1005a907181ba7410596022594182 |
| NCN | NICKEL CYANIDE | 氰化镍 | 557-19-7 |  | pdf_6a8faacca882a39304796eef402a5436_e50ced0f65223b044adc38ed48d78a4f7410596022594182 |
| NCS | NICOTINE SULFATE | 硫酸烟碱 | 65-30-5 | Black leaf 40 (40% watersolution)Neutral nicotine sulfate | pdf_6a8faacca882a39304796eef402a5436_46108305b691f8197fa2d1f44fa076127410596022594182 |
| NCT | NAPHTHA: COAL TAR | 煤焦油石脑油 |  | Mixture of benzene, toluene,xylenes | pdf_6a8faacca882a39304796eef402a5436_25a63a450ffc6ae14947b4677090e72f7410596022594182 |
| NEA | NEODECANOIC ACID | 新癸酸 |  | 2.2-Dimethyl octanoic acid | pdf_6a8faacca882a39304796eef402a5436_e313e77afcb62ca838474b8aa220363b7410596022594182 |
| NFB | NICKEL FLUOROBORATE | 氟硼酸镍 | 14708-14-6 | Nickel (ii) fluoborateNickel fluoroborate solution | pdf_6a8faacca882a39304796eef402a5436_257b9d5f2cf6ad22a2a23b968653f9c67410596022594182 |
| NFM | NICKEL FORMATE | 甲酸镍 | 15843-02-4 | Nickel formate dihydrate | pdf_6a8faacca882a39304796eef402a5436_83e137f39ecae0971e82e021f47352057410596022594182 |
| NHX | NEOHEXANE | 新己烷 | 75-83-2 | 2.2-Dimethylbutane | pdf_6a8faacca882a39304796eef402a5436_6205e1e14d3908bd884170ff50c1f8c87410596022594182 |
| NIC | NICOTINE | 烟碱（尼古丁） | 54-11-5 | 1-Methyl-2-(3-pyridjypyrmoldine3-(1-Methyl-2-pyrroidjypjryindineMixes with water | pdf_6a8faacca882a39304796eef402a5436_2594634717046e388513912fea3474217410596022594182 |
| NIE | O-NITROTOLUENE | 邻硝基甲苯 | 88-72-2 | 2-Methyl nitrobenzene2-NitrofolueneToluene, o-nitro | pdf_6a8faacca882a39304796eef402a5436_613b2960c40d4b620790b0599f4078d77410596022594182 |
| NIP | 3-NITROPHENOL | 3-硝基苯酚 | 554-84-7 | 3-Hydroxynitrobenzanem-Hydroxynitrobenzamenm-Nitrophenol | pdf_6a8faacca882a39304796eef402a5436_2cd0ca52b98a83d85ef9d10a0281a3107410596022594182 |
| NKA | NICKEL ACETATE | 乙酸镍 | 373-02-4 | Acetic acid, nickel (II) saltNickel acetate tetrahyrateNickelous acetate | pdf_6a8faacca882a39304796eef402a5436_6d9d37924d74fe57188268391c01d63c7410596022594182 |
| NKC | NICKEL CARBONYL | 羰基镍 | 13463-39-3 | Nickel tetrarcarbony | pdf_6a8faacca882a39304796eef402a5436_5867715f8b90bb4b4ba3fad8861368547410596022594182 |
| NKH | NICKEL HYDROXIDE | 氢氧化镍 | 12054-48-7 | Green nickel oxideNickel dhydroxideNickelous hydroxide | pdf_6a8faacca882a39304796eef402a5436_52ab7f0a721d2963819d56ec57847d0b7410596022594182 |
| NKS | NICKEL SULFATE | 硫酸镍 | 7786-81-4 | Nickelous sulfate | pdf_6a8faacca882a39304796eef402a5436_442e0010e45ba15548f1b9dbfe694d6d7410596022594182 |
| NLD | NALED | 二溴磷 | 300-76-5 |  | pdf_6a8faacca882a39304796eef402a5436_b9c3b69be095a182c3ee513a7d30628a7410596022594182 |
| NMT | NITROMETHANE | 硝基甲烷 | 75-52-5 |  | pdf_6a8faacca882a39304796eef402a5436_c699c883c621df5473e3f1ac30c7af3e7410596022594182 |
| NNE | 1-NONENE | 1-壬烯 | 124-11-8 | n-Heptyletylenen-1-Nylonene | pdf_6a8faacca882a39304796eef402a5436_b788e50ff458f2ce9aa98f63860412ce7410596022594182 |
| NNN | NONANOL | 壬醇 | 143-08-8 | 1-NonanolNonyl alcoholNonyl alcohol/pelargonic alcoholOctycarbinol | pdf_6a8faacca882a39304796eef402a5436_a8e94509ff701d27c9a13e2557c752967410596022594182 |
| NNP | NONYLPHENOL | 壬基苯酚 | 25154-52-3 |  | pdf_6a8faacca882a39304796eef402a5436_b79205ed70fa9d6252390f46e1cae5507410596022594182 |
| NNT | NICKEL NITRATE | 硝酸镍 | 13138-45-9 | Nickel nitrate hexahydrate | pdf_6a8faacca882a39304796eef402a5436_3813522cee91b1420a2f272c852f036f7410596022594182 |
| NON | NONENE | 壬烯 | 124-11-8 | Nonene (nonlinearPropylene trimerTripropylene | pdf_6a8faacca882a39304796eef402a5436_8e55f6d29877061f82fa70148c826f477410596022594182 |
| NOX | NITROGEN TETROXIDE | 四氧化二氮 | 10544-72-6 | Dinitrogen troxidexNitrogen dioxideXidrogen peroxideOxides of nitrogenRed oxide  | pdf_6a8faacca882a39304796eef402a5436_0e28640dd90140deec0a5607913aa3517410596022594182 |
| NPH | 4-NITROPHENOL | 4-硝基苯酚 | 100-02-7 | 4-Hydroxynitrobenzenep-NitrophenolPNP | pdf_6a8faacca882a39304796eef402a5436_003279e9d599fa3137b1774a3053d2297410596022594182 |
| NPN | 1-NITROPANE | 1-硝基丙烷 |  | Propane, 1-nitro- | pdf_6a8faacca882a39304796eef402a5436_d6a548257066e2aeef2ef6e1b8cabb7e7410596022594182 |
| NPP | 2-NITROPROPANE | 2-硝基丙烷 | 79-46-9 |  | pdf_6a8faacca882a39304796eef402a5436_d87c06325649fa2cee6aa95c6cd85b057410596022594182 |
| NSS | NAPHTHA: STODDARD SOLVENT | 斯陶达溶剂石脑油 |  | Drycleaner napthtaPetroleum solventSpotting napthha | pdf_6a8faacca882a39304796eef402a5436_ddcd8aeb9667af2af6ed70c1d6ef30697410596022594182 |
| NSV | NAPHTHA: SOLVENT | 溶剂石脑油 |  | Light napthaPetroleum solvent | pdf_6a8faacca882a39304796eef402a5436_55edc288184bb9bac24ce46a0ceb10637410596022594182 |
| NTA | 2-NITROANILINE | 2-硝基苯胺 | 88-74-4 | 1-Amino-2-nitrobenzeneAzoic diazo component 6o-Nitranilineo-NitranilineONA | pdf_6a8faacca882a39304796eef402a5436_677546f76f8d5db089dc54eee0f3bbb37410596022594182 |
| NTB | NITROBENZENE | 硝基苯 | 98-95-3 | Essence of mirbaneNitrobenzolOil of mirbane | pdf_6a8faacca882a39304796eef402a5436_fd3e7b87b9536bd7cf91671d45e607bd7410596022594182 |
| NTC | NITROSYL CHLORIDE | 亚硝酰氯 | 2696-92-6 |  | pdf_6a8faacca882a39304796eef402a5436_e1cfd9b4cbda301a71148b49fe7afe417410596022594182 |
| NTE | NITROETHANE | 硝基乙烷 | 79-24-3 |  | pdf_6a8faacca882a39304796eef402a5436_f482240f4244bf841486c082a46269867410596022594182 |
| NTI | NAPHTHENIC ACIDS | 环烷酸 |  |  | pdf_6a8faacca882a39304796eef402a5436_b91ee81141d8446e72eb8c119ec1fea17410596022594182 |
| NTL | NITRALIN | 氟乐灵 | 4726-14-1 | N.N-Dipropyaniline4-(Methylsulfonyl)-2,6-dintroPlanavin | pdf_6a8faacca882a39304796eef402a5436_164845f58569bd96acaafa033e0d35ce7410596022594182 |
| NTM | NAPHTHALENE | 萘 | 91-20-3 | NaphthalinTar camphor | pdf_6a8faacca882a39304796eef402a5436_1fd25ddaa042060ddb413338a22f38cc7410596022594182 |
| NTO | NITROUS OXIDE | 一氧化二氮（笑气） | 10024-97-2 | Dinitrogen monoxideLaughing gas | pdf_6a8faacca882a39304796eef402a5436_ab46df1e8eedfdc4426b685e637f752a7410596022594182 |
| NTP | 2-NITROPHENOL | 2-硝基苯酚 | 88-75-5 | 2-Hydroxynitrobenzeneo-NitrophenolONP | pdf_6a8faacca882a39304796eef402a5436_f5f2c92633e23cff985a0993302659587410596022594182 |
| NTR | M-NITROTOLUENE | 间硝基甲苯 | 99-08-1 | 3-Methyl nitrobenzene3-Nitrotoluene3-Nitrotoluene | pdf_6a8faacca882a39304796eef402a5436_c54531074d6c5b35c26708a1bc5672387410596022594182 |
| NTT | P-NITROTOLUENE | 对硝基甲苯 | 99-99-0 |  | pdf_6a8faacca882a39304796eef402a5436_8c4da2c21179ae8fdf250a1258b6e6a67410596022594182 |
| NTX | NITRIC OXIDE | 一氧化氮 | 10102-43-9 | Mononitrogen monoxide Nitrogen monoxide | pdf_6a8faacca882a39304796eef402a5436_67eee3f5679092c6882d50802fce11037410596022594182 |
| NVM | NAPHTHA: VM & P | VM&P石脑油 |  | Light naphthaPainter&#x27 s naphthaPetroleum solvent | pdf_6a8faacca882a39304796eef402a5436_8b91f12aaddea45f7583e506a8e3dc757410596022594182 |
| NXX | NITROGEN | 氮 | 7727-37-9 | Liquid nitrogen | pdf_6a8faacca882a39304796eef402a5436_792b8ec3eb169dcaf7d1ad3ac35759c47410596022594182 |
| OAA | OCTANOIC ACID | 辛酸 | 124-07-2 |  | pdf_6a8faacca882a39304796eef402a5436_6608677d665ef018e16711b7f910a0637410596022594182 |
| OAC | OLEIC ACID, SODIUM SALT | 油酸钠 | 143-19-1 |  | pdf_6a8faacca882a39304796eef402a5436_a55ceb12833362acd35aefe907bbaac87410596022594182 |
| OAL | OCTYL ALDEHYDES | 辛醛 | 124-13-0 | 1-Octalann-Octyl aldehyde | pdf_6a8faacca882a39304796eef402a5436_c28fff8cc5ff0b5510aa0c4fc6744bd17410596022594182 |
| OAN | OCTANE | 辛烷 | 111-65-9 | n-Octane | pdf_6a8faacca882a39304796eef402a5436_5e70e3c492bc0ed14db89ec4a167fcbf7410596022594182 |
| OAP | OLEIC ACID, POTASSIUM S | 油酸钾 |  | Potassium oleate | pdf_6a8faacca882a39304796eef402a5436_0de33b3656eecf6cdf328c049d9b0a7a7410596022594182 |
| OAS | OILS, MISCELLANEOUS: ABSORPTION | 吸收油 |  | Absorbent oil | pdf_6a8faacca882a39304796eef402a5436_fa172386a20ebc3a3398c858321abaf47410596022594182 |
| OCA | OILS, EDIBLE: CASTOR | 蓖麻油 |  |  | pdf_6a8faacca882a39304796eef402a5436_7c8856615d6a49e3833452a17c5d09587410596022594182 |
| OCC | OILS, EDIBLE: COCONUT | 椰子油 |  | Coconut butterCoconut oilCopra oil | pdf_6a8faacca882a39304796eef402a5436_8c9898ef47473ad25f9b4bfd7f8c2d367410596022594182 |
| OCF | OILS: CLARIFIED | 澄清油 |  |  | pdf_6a8faacca882a39304796eef402a5436_179644d3bbb82141a03dea77e3f8f2ee7410596022594182 |
| OCN | OIL, MISC: CASHEW NUT SHELL | 腰果壳油 |  |  | pdf_6a8faacca882a39304796eef402a5436_fdc7acc531f35134b6842ec26aa044437410596022594182 |
| OCR | OILS, MISCELLANEOUS: CROTON | 巴豆油 |  |  | pdf_6a8faacca882a39304796eef402a5436_698ea3aedbca5a613eff72ecebc526507410596022594182 |
| OCS | OILS, EDIBLE: COTTONSEEDocs | 棉籽油 |  |  | pdf_6a8faacca882a39304796eef402a5436_85362c7ed5b44b4065a7bb9929f0a5b57410596022594182 |
| OCT | OILS, MISCELLANEOUS: COAL TAR | 煤焦油 |  | Light oil | pdf_6a8faacca882a39304796eef402a5436_d36d72b6a3b69624718c3fbe9aab73e17410596022594182 |
| ODP | OCTYL DECYL PHTHALATE | 邻苯二甲酸辛癸酯 | 119-07-3 | n-Octyl-n-decyl phthalate | pdf_6a8faacca882a39304796eef402a5436_598837157597e42a37e817db9d79e40b7410596022594182 |
| ODS | OILS: DIESEL | 柴油 |  | Fuel oil 1-DFuel oil 2-D | pdf_6a8faacca882a39304796eef402a5436_84dc3d76c28bbcb7b9a14111afb2158b7410596022594182 |
| OET | OCTYL EPOXY TALLATE | 环氧妥尔油酸辛酯 |  | Epoxidized tall oil, octyl ester | pdf_6a8faacca882a39304796eef402a5436_7b71b87e0860dcd00651153af7569c727410596022594182 |
| OFR | OILS, FUEL: 4 | 4号燃料油 |  | No. 4Residual fuel oil | pdf_6a8faacca882a39304796eef402a5436_75249b51073c1397aca45751a7263d457410596022594182 |
| OFS | OILS, EDIBLE: FISH | 鱼油 |  |  | pdf_6a8faacca882a39304796eef402a5436_210ba56542cff2701abd06c7f01baede7410596022594182 |
| OFV | OILS, FUEL: 5 | 5号燃料油 |  | No. 5Residual fuel oil | pdf_6a8faacca882a39304796eef402a5436_293fb0d920e9fb0d15f23f27197405897410596022594182 |
| OIL | OILS: CRUDE | 原油 |  | Petroleum | pdf_6a8faacca882a39304796eef402a5436_17cb3c139a8c60abac99a3f02ba1b4a57410596022594182 |
| OLA | OLEIC ACID | 油酸 | 112-80-1 | cis-8-Heptadecynecarboxylicacidcis-9-Octadecneol acidRed oil | pdf_6a8faacca882a39304796eef402a5436_face6d6b222e594045957a9309e2bf7c7410596022594182 |
| OLB | OILS, MISCELLANEOUS: LUBRICATING | 润滑油 |  | Crankcase oilMotor oilTransmission oil | pdf_6a8faacca882a39304796eef402a5436_ec0646e750b33a642e76d2d6760d4ae07410596022594182 |
| OLD | OILS, EDIBLE: LARD | 猪油 |  | Kettle rendered lardLardLeaf lardPrime steam lard | pdf_6a8faacca882a39304796eef402a5436_c885474312ca040639d40efc357632f07410596022594182 |
| OLM | OLEUM | 发烟硫酸 | 8014-95-7 | Fuming sulfuric acid | pdf_6a8faacca882a39304796eef402a5436_780f6cd007ddf2da60c20b73bf6565037410596022594182 |
| OLS | OILS, MISCELLANEOUS: LINSEED | 亚麻籽油 |  |  | pdf_6a8faacca882a39304796eef402a5436_a90b459f65f2544b49375cac23e1ae567410596022594182 |
| OMN | OILS, MISCELLANEOUS: MINERAL | 矿物油 |  | Liquid petrolatumWhite oil | pdf_6a8faacca882a39304796eef402a5436_bc7a2034d36e8cae6b70b5c7d33cefb47410596022594182 |
| OMS | OILS, MISCELLANEOUS: MINERAL SEAL | 矿物密封油 |  | Long-time burning oilMineral colza oil300o OilSignal oil | pdf_6a8faacca882a39304796eef402a5436_f42fa61df48051ad566e2798cb6dbe8f7410596022594182 |
| OMT | OILS, MISCELLANEOUS: MOTOR | 机油 |  | Crankcase oilLubricating oilTransmission oil | pdf_6a8faacca882a39304796eef402a5436_7f9427046d6c3779a5e245e0c56eb3fa7410596022594182 |
| ONF | OILS, MISCELLANEOUS: NEATSFOOT | 牛脚油 |  |  | pdf_6a8faacca882a39304796eef402a5436_49709d5fed2fb5e56f5ce6536b3cafb47410596022594182 |
| ONN | OILS, FUEL: NO. 1 | 1号燃料油 |  |  | pdf_6a8faacca882a39304796eef402a5436_c90a0bbc014f6346501198a9f2d2a4927410596022594182 |
| OOD | OILS, FUEL: 1-DOOD|CAUTIONARY RESPONSE INFORMATION|||||---|---|---|---||Common SynonymsDiesel oil (light)|Oily liquid|Yellow-brown|Lube or fuel oil odor|||Floats on water.|Floats on water.|Floats on water.||Keep people away. Avoid contact with liquid.Shut off ignition sources and call fire d | 1-D号燃料油（轻柴油） |  | Diesel oil (light) | pdf_6a8faacca882a39304796eef402a5436_43bc20554845d19c14fd858c1e99412b7410596022594182 |
| OOL | OILS, EDIBLE: OLIVE | 橄榄油 |  |  | pdf_6a8faacca882a39304796eef402a5436_d991326aae9e4f842a720436721f3c967410596022594182 |
| OON | OILS, FUEL: NO. 1 | 1号燃料油 |  |  | pdf_6a8faacca882a39304796eef402a5436_74bd02a094e9a9ead0166b8d2206e1b77410596022594182 |
| OPI | OIL, MISC: PINE | 松油 |  |  | pdf_6a8faacca882a39304796eef402a5436_73575a4e5ae04051ac621f56b79473d47410596022594182 |
| OPM | OILS, EDIBLE: PALM | 棕榈油 |  |  | pdf_6a8faacca882a39304796eef402a5436_78effcf547834fae4b839bf48256b4397410596022594182 |
| OPN | OILS, EDIBLE: PEANUT | 花生油 |  |  | pdf_6a8faacca882a39304796eef402a5436_019ce4791128ad5b0ce5e606ba3732767410596022594182 |
| OPT | OILS, MISCELLANEOUS: PENETRATING | 渗透油 |  | Preservative oilWater displacing oil | pdf_6a8faacca882a39304796eef402a5436_36c41df00855cf720c20937e2e9ba8797410596022594182 |
| ORD | OILS, MISCELLANEOUS: ROAD | 道路油 |  | Liquid asphaltPetroleum asphaltSlow curing asphalt | pdf_6a8faacca882a39304796eef402a5436_7f2f5a51d92e5cffb84a4c789e8f97b67410596022594182 |
| ORG | OILS, MISCELLANEOUS: RANGE | 日用油 |  |  | pdf_6a8faacca882a39304796eef402a5436_6280fdbd37ddf5cf6773365719c6080e7410596022594182 |
| ORN | OILS, MISCELLANEOUS: ROSIN | 松香油 |  |  | pdf_6a8faacca882a39304796eef402a5436_1e991b2cf1a2530e544e5734916821dd7410596022594182 |
| ORS | OILS, MISCELLANEOUS: RESIN | 树脂油 |  |  | pdf_6a8faacca882a39304796eef402a5436_c263d2aaa19ed41f68fb3175384ab5f57410596022594182 |
| OSB | OILS, EDIBLE: SOYA BEAN | 大豆油 |  | Soybean oil | pdf_6a8faacca882a39304796eef402a5436_d66577aee4d7a4855cbf10373de6431a7410596022594182 |
| OSD | OILS, MISCELLANEOUS: SPINDLE | 锭子油 |  |  | pdf_6a8faacca882a39304796eef402a5436_82eb36ee6dbe22e5c3dca368d71be7a07410596022594182 |
| OSF | OILS, EDIBLE: SAFFLOWER | 红花油 |  | Carthamus tinctorius oilSafflower oilSafflower seed oil | pdf_6a8faacca882a39304796eef402a5436_d1a538d6057a210ac48795244391d5f67410596022594182 |
| OSP | OILS, MISCELLANEOUS: SPERM | 鲸油 |  |  | pdf_6a8faacca882a39304796eef402a5436_58a1760f15e7ed99e2144d78f08aed677410596022594182 |
| OSX | OILS, FUEL: NO. 6osx | 6号燃料油 |  | Bunker C oillNo. 6Residual fuel oil | pdf_6a8faacca882a39304796eef402a5436_18b59fe6e74e25df4cfd8ef24e30f9ee7410596022594182 |
| OSY | OILS, MISCELLANEOUS: SPRAYosy | 喷雾油 |  | Dormant oilPollage oilKerocene, heavyPlant spray oil | pdf_6a8faacca882a39304796eef402a5436_25009afc47f8cc0eaba6c779d43567e87410596022594182 |
| OTA | OCTANOL | 辛醇 | 111-87-5 | Alcohol C-8Heptycarbinol1-OctanolOctyl alcohol | pdf_6a8faacca882a39304796eef402a5436_0ba2cb708ee7245b65f85e5c51a3389d7410596022594182 |
| OTB | OILS, MISCELLANEOUS: TURBINE | 透平油 |  | Steam turbine tube oilSteam turbine oilTurbine oil | pdf_6a8faacca882a39304796eef402a5436_27b79e0c537589a5a6452ce8200dd6ac7410596022594182 |
| OTC | OILS, EDIBLE: TUCUM | 土库姆油 |  | American palm kernel oilAquara oilPalm seed oilTucum oil | pdf_6a8faacca882a39304796eef402a5436_bb510f25d6d8c926442bbed68f9207437410596022594182 |
| OTD | OILS, FUEL: 2-D | 2-D号燃料油（柴油） |  | Diesel oil, medium | pdf_6a8faacca882a39304796eef402a5436_92fdd1b464c4c4490f2c3f61bd3b2eea7410596022594182 |
| OTE | 1-OCTENE | 1-辛烯 | 111-66-0 | Caprylene alpha-Octylene | pdf_6a8faacca882a39304796eef402a5436_b4f8137993429d16313a9cce1fb4e6587410596022594182 |
| OTF | OILS, MISCELLANEOUS: TRANSFORMER | 变压器油 |  | Electrical insulating oilInsulating oilPetroleum insulating oil | pdf_6a8faacca882a39304796eef402a5436_833a40e3a22f81414f3287653205cbff7410596022594182 |
| OTL | OILS, MISCELLANEOUS: TALL | 妥尔油 |  |  | pdf_6a8faacca882a39304796eef402a5436_5ae2531e94a3c5a562d7954e924482c77410596022594182 |
| OTN | OILS, MISCELLANEOUS: TANNER'S | 鞣革油 |  | Sulfated neatsfoot oil | pdf_6a8faacca882a39304796eef402a5436_31577202d07428d76cde09a72bf60ad17410596022594182 |
| OTW | OILS, FUEL: 2 | 2号燃料油 |  | Home-heating oil | pdf_6a8faacca882a39304796eef402a5436_b31e9ad13096c6a0d70346ddf8dcb2827410596022594182 |
| OVG | OILS, EDIBLE: VEGETABLEovg | 植物油 |  |  | pdf_6a8faacca882a39304796eef402a5436_ae57617b00f8991c1544b9f71d0325527410596022594182 |
| OXA | OXALIC ACID | 草酸 | 144-62-7 | Ethanedioic acid | pdf_6a8faacca882a39304796eef402a5436_d3fa8a58cce6d5f2d42cc6cbb393ce5a7410596022594182 |
| OXY | OXYGEN | 氧 | 7782-44-7 | Liquid oxygenLOX | pdf_6a8faacca882a39304796eef402a5436_be534641b48a7d43e27cc049eb9b0b3d7410596022594182 |
| PAA | PERACETIC ACID | 过氧乙酸 | 79-21-0 | Acetyl hydroperoxidePeroxyacetic acid | pdf_6a8faacca882a39304796eef402a5436_55bf61c10d44d010b4b8fc4a11c735dc7410596022594182 |
| PAC | PHOSPHORIC ACID | 磷酸 | 7664-38-2 | Orthophosphoric acid | pdf_6a8faacca882a39304796eef402a5436_05a394575c5b6df00b75deb4b0da195f7410596022594182 |
| PAD | PROPIONALDEHYDE | 丙醛 | 123-38-6 |  | pdf_6a8faacca882a39304796eef402a5436_33d092c8c86d1ee1e8b4b77bc7ca647d7410596022594182 |
| PAH | PROPIONIC ANHYDRIDE | 丙酸酐 | 123-62-6 | Methylacetic anhydridePropanolic anhydrideProplyin | pdf_6a8faacca882a39304796eef402a5436_a0e8fc78a06594e37248ce28c90c175c7410596022594182 |
| PAL | N-PROPYL ALCOHOL | 正丙醇 | 71-23-8 |  | pdf_6a8faacca882a39304796eef402a5436_836977330e4d04ce26df63e7ecf2a2b87410596022594182 |
| PAM | 2-PROPANOLAMINE | 2-丙醇胺 |  |  | pdf_6a8faacca882a39304796eef402a5436_00191768027c23700291d0c2bfa595907410596022594182 |
| PAN | PHTHALIC ANHYDRIDE | 邻苯二甲酸酐 | 85-44-9 | 1.2-Benzenedcarboxylic acidanthridide1.3-DioxophthalanPANPhthalandonePhthalic ac | pdf_6a8faacca882a39304796eef402a5436_b7d575be9236ab9371aad2aa9cf9d5f97410596022594182 |
| PAS | POTASSIUM ARSENATE | 砷酸钾 | 7784-41-0 | Macquer saltPotassium acid arsenatePotassium dihydrogen arsenate | pdf_6a8faacca882a39304796eef402a5436_adb16ce5e35472f1d19483a0ede1a2477410596022594182 |
| PAT | N-PROPYL ACETATE | 乙酸正丙酯 | 109-60-4 | Acetic acid, n-propyl ether | pdf_6a8faacca882a39304796eef402a5436_9c7169e99fc5116fd9367f18fd3531b57410596022594182 |
| PBO | POTASSIUM BINOXALATE | 草酸氢钾 | 127-95-7 | Potassium acid oxalateSal acetosellaSalt of sorrel | pdf_6a8faacca882a39304796eef402a5436_c09b0df88349f3e4160e43a93289d4787410596022594182 |
| PBP | PROPYLENE BUTYLENE POLYMER | 丙烯-丁烯聚合物 |  |  | pdf_6a8faacca882a39304796eef402a5436_af4ef1823de2176dfcdd8784eb385f617410596022594182 |
| PBR | PHOSPHORUS TRIBROMIDE | 三溴化磷 | 7789-60-8 | Phosphorus bromide | pdf_6a8faacca882a39304796eef402a5436_21f01fff154115b0f84f13cfb74d06177410596022594182 |
| PBZ | N-PROPYLBENZENE | 正丙苯 | 103-65-1 |  | pdf_6a8faacca882a39304796eef402a5436_f15c6a7cdc30426fe2c07576b94f5dbf7410596022594182 |
| PCB | POLYCHORINATED BIPHENYL | 多氯联苯（PCB） |  |  | pdf_6a8faacca882a39304796eef402a5436_ac5933b38bdb54e9acfa53af21e84e8a7410596022594182 |
| PCE | PENTACHLOROETHANE | 五氯乙烷 | 76-01-7 | Ethane pentachlorideEthane, pentachloro-Pentalin | pdf_6a8faacca882a39304796eef402a5436_8d4185229f5b682320946f97fd916ce77410596022594182 |
| PCH | POTASSIUM CHROMATE | 铬酸钾 | 7789-00-6 | Neutral potassium chromatePotassium chromate (V) | pdf_6a8faacca882a39304796eef402a5436_e41abff26f177d7cd887ee69dbf4ae4d7410596022594182 |
| PCL | PERCHLORIC ACID | 高氯酸 | 7601-90-3 | Dioxonium perchlorate solutionPerchloric acid solution | pdf_6a8faacca882a39304796eef402a5436_c969f49c5120b7a059959cebc4d1f9a97410596022594182 |
| PCM | PERCHLOROMETHYL MERCAPTAN | 全氯甲硫醇 | 594-42-3 | Thiocarbonyl tetrachlorideTrichloromethyl suffur chloridtrichloromethanesullenyl | pdf_6a8faacca882a39304796eef402a5436_e6d6f0b0ce9b2d5053cb1ce09a3e59457410596022594182 |
| PCN | PROPIONITRILE | 丙腈 | 107-12-0 |  | pdf_6a8faacca882a39304796eef402a5436_20f38cf42934dd0c53b6b6aabdcdd18f7410596022594182 |
| PCP | PENTACHLOROPHENOL | 五氯苯酚 | 87-86-5 | Dowicide 7PentaSantophent 20 | pdf_6a8faacca882a39304796eef402a5436_31aee362d98ceab2bd68d626003eb6237410596022594182 |
| PCR | POTASSIUM CHLORATE | 氯酸钾 | 3811-04-9 | Chlorate of potashChlorate of potassiumPotrate | pdf_6a8faacca882a39304796eef402a5436_6331253bf12b150a704e43421edcec767410596022594182 |
| PDC | PENTADECANOL | 十五醇 | 31389-11-4 | 1-PentadecanolPentadecyl alcohol | pdf_6a8faacca882a39304796eef402a5436_eff8f43a09898be3b7b7df9a0fa21de07410596022594182 |
| PDE | 1,3-PENTADIENE | 1,3-戊二烯 | 504-60-9 | alpha-Methylbutinyl1-Methylbutinielcis-Pentandiene-1,3Trans-Pentadiene-1,3Pipery | pdf_6a8faacca882a39304796eef402a5436_4394c42ba59b6722766ee405db03cc227410596022594182 |
| PDH | PARALDEHYDE | 三聚乙醛 | 123-63-7 | p-Acetaldehyde Paracetaldehyde 2, 6-Trimethyl-1, 3, 5-bioxane | pdf_6a8faacca882a39304796eef402a5436_86cc6188f7607098deaf4e5ffa7db4c57410596022594182 |
| PDL | PHENYLDICHLOROARSINE | 苯基二氯化胂 | 696-28-6 | Pherylarsenic dichloride | pdf_6a8faacca882a39304796eef402a5436_9aab1a68bc44d708f159bf899bb9c8077410596022594182 |
| PDN | 1,4-PENTADIENE | 1,4-戊二烯 | 591-93-5 |  | pdf_6a8faacca882a39304796eef402a5436_d5333e3c7556da08bf780778b962e8a47410596022594182 |
| PDT | POTASSIUM DICHLORO-S-TRIAZINETRIONE | 二氯异氰尿酸钾 | 2244-21-5 | Potassium dichloroisocyanurate | pdf_6a8faacca882a39304796eef402a5436_513314334c101ee542418b5d22e9c03d7410596022594182 |
| PEB | POLYETHYLENE POLYAMINES | 聚乙烯多胺 |  | (Poly(ethyleneimine) Poly(ethyleneimine) | pdf_6a8faacca882a39304796eef402a5436_81c38c12761732dd07e2e626799b528b7410596022594182 |
| PEN | PENTAETHYLENEHEXAMINE | 五乙烯六胺 | 4067-16-7 | Levepox hardener T33.6.9.12-Tetraazetradecane-1.14-diamine | pdf_6a8faacca882a39304796eef402a5436_d88c4f072989617b8afee9f652d0b6587410596022594182 |
| PET | PENTAERYTHRITOL | 季戊四醇 | 115-77-5 | 2.2-bis(Hydroxymethyly)-1,3-propanediolMono PEPEPentayrthritePentakTetrahydroxym | pdf_6a8faacca882a39304796eef402a5436_7ea465dad662dfcbb99a6607536fbd9f7410596022594182 |
| PFA | PARAFORMALDEHYDE | 多聚甲醛 |  | Formaldehyde polymerPolyformaldehydePolyformalethylenePolyoxymethylene glycol | pdf_6a8faacca882a39304796eef402a5436_ec64b389a4d78fd4f4816a4dddb1742b7410596022594182 |
| PGA | PYROGALLIC ACID | 焦性没食子酸 | 87-66-1 | 1.2.3-BenzenetrolPyrogalol1.2,3-Trihydroxybenzene | pdf_6a8faacca882a39304796eef402a5436_3545564c63c36f3f1282b37888e4be0b7410596022594182 |
| PGC | POLYPROPYLENE GLYCOL | 聚丙二醇 |  |  | pdf_6a8faacca882a39304796eef402a5436_8f7a5fc9d40d4267a7f4d3f2e2ee542c7410596022594182 |
| PGM | POLYPROPYLENE GLYCOL METHYL ETHER | 聚丙二醇甲醚 |  | Poloxypropylene glycol methylotherPoly (propylene glycol) methylother | pdf_6a8faacca882a39304796eef402a5436_512d15faf2e84448803330c00cbcfc137410596022594182 |
| PGN | PROPYLENE GLYCOL METHYL ETHER ACETATE | 丙二醇甲醚乙酸酯 | 108-65-6 | 1-Methoxy-2-propanol acetate | pdf_6a8faacca882a39304796eef402a5436_b7b90c003b763dfa2777860505167d307410596022594182 |
| PGY | PROPYLENE GLYCOL ETHYL ETHER | 丙二醇乙醚 | 1569-02-4 | 1-Ethoxy-2-propanol | pdf_6a8faacca882a39304796eef402a5436_372a22df627ebdb16f237a54d3cb65987410596022594182 |
| PHD | PHOSDRIN | 速灭磷 | 7786-34-7 |  | pdf_6a8faacca882a39304796eef402a5436_8ca405a101c38f839a1342eed8039d317410596022594182 |
| PHE | PHENYLHYDRAZINE | 苯肼 | 100-63-0 |  | pdf_6a8faacca882a39304796eef402a5436_1553ccd1b6f0a1a85a746cd8369310177410596022594182 |
| PHG | PHOSGENE | 光气（碳酰氯） | 75-44-5 | Carbonyl chlorideChloroformyl chloride | pdf_6a8faacca882a39304796eef402a5436_72b7c2171648d46d65f1e451758ba5037410596022594182 |
| PHH | PHENYLHYDRAZINE HYDROCHLORIDE | 苯肼盐酸盐 | 59-88-1 | Phenylydrazinium chloride | pdf_6a8faacca882a39304796eef402a5436_233751e79f36cc0f7075bb8205387efe7410596022594182 |
| PHN | PHENOL | 苯酚 | 108-95-2 |  | pdf_6a8faacca882a39304796eef402a5436_057d81bf96b7e229fb0a7af40419832c7410596022594182 |
| PII | PROPYLENEIMINE | 丙撑亚胺 | 75-55-8 | 2-Methylziridine2-Methylethyleneimine | pdf_6a8faacca882a39304796eef402a5436_93290bdf08906675facfc5b74a2748a07410596022594182 |
| PIN | PINENE | 蒎烯 |  |  | pdf_6a8faacca882a39304796eef402a5436_b286b0d09eb682b4464f54fc32b345df7410596022594182 |
| PLA | N-PROPANOLAMINE | 正丙醇胺 | 156-87-6 | 3-Amino-1-propanol3-Propanolaminine1-Propanol, 3-amino | pdf_6a8faacca882a39304796eef402a5436_cd74743f8e51f26eeb8c824ffe665d657410596022594182 |
| PLB | POLYBUTENE | 聚丁烯 |  |  | pdf_6a8faacca882a39304796eef402a5436_63934cf48f2d3a754fcb4294996f90db7410596022594182 |
| PLP | POLYPROPYLENE | 聚丙烯 |  | Propene polymer | pdf_6a8faacca882a39304796eef402a5436_7ab0a260ee8c8a7bff76950a278004ee7410596022594182 |
| PLT | BETA-PROPIOLACTONE | β-丙内酯 | 57-57-8 |  | pdf_6a8faacca882a39304796eef402a5436_e1f881b5622d67da25b7318e506724de7410596022594182 |
| PMA | PHENYLMERCURIC ACETATE | 乙酸苯汞 | 62-38-4 | Acetatophenylmercury(Acetato-o) phenyl mercuryCocure 26Cosan PMA-100 | pdf_6a8faacca882a39304796eef402a5436_a6a770e97b039e134d7e22673b84e9877410596022594182 |
| PME | PROPYLENE GLYCOL METHYL ETHER | 丙二醇甲醚 | 1320-67-8 |  | pdf_6a8faacca882a39304796eef402a5436_f695ba336a01bc08c36ba347de0e89d77410596022594182 |
| PMN | N-PROPYL MERCAPTAN | 正丙硫醇 | 107-03-9 |  | pdf_6a8faacca882a39304796eef402a5436_2ab47190e1c8bc031b0fe9e3777404327410596022594182 |
| PNA | PROPIONIC ACID | 丙酸 | 79-09-4 | Ethanecarboxy acidMethylacetic acidPropanoic acid | pdf_6a8faacca882a39304796eef402a5436_57ba70ca776debb0bc15bfaecf6883c67410596022594182 |
| PNE | 2-PENTANONE | 2-戊酮 | 107-87-9 | Ethyl acetoneMethyl n-propyl ketone | pdf_6a8faacca882a39304796eef402a5436_23700cd82fa41d4a0233c4f062cec76f7410596022594182 |
| PNI | N-PROPYL NITRATE | 硝酸正丙酯 | 627-13-4 |  | pdf_6a8faacca882a39304796eef402a5436_4b85406e1d7715e2786d7eafbdac359e7410596022594182 |
| PNR | POTASSIUM NITRATE | 硝酸钾 | 7757-79-1 | Dexol stump removerPotash nitrateSaltpeter | pdf_6a8faacca882a39304796eef402a5436_800fd406d9d79892d368db667a0a4b947410596022594182 |
| POA | POTASSIUM ARSENITE | 亚砷酸钾 | 10124-50-2 | Arsenious acid, potassium saltFowlers solutionPotassium metaarsenite | pdf_6a8faacca882a39304796eef402a5436_305aac29c277cb478e602e8a5c27f7857410596022594182 |
| POC | PENTANOIC ACID | 戊酸 | 109-52-4 | Valeric acid | pdf_6a8faacca882a39304796eef402a5436_057deaf8e760567d546d2eeb7e127f6c7410596022594182 |
| POE | POTASSIUM OLEATE | 油酸钾 | 143-18-0 | Potash soap | pdf_6a8faacca882a39304796eef402a5436_42189364665cc18ea9ae6bd3dc69b43c7410596022594182 |
| POP | POTASSIUM PEROXIDE | 过氧化钾 | 17014-71-0 | Potassium superoxide | pdf_6a8faacca882a39304796eef402a5436_9303e7760a0a700429b7a12e1992ea6f7410596022594182 |
| POX | PROPYLENE OXIDE | 环氧丙烷 | 75-56-9 | 1.2-EpoxpropaneMethyloxiranePropeneoxide | pdf_6a8faacca882a39304796eef402a5436_f0cdff62d241daa48e2a4766a22a20817410596022594182 |
| PPA | POLYPHOSPHORIC ACID | 多聚磷酸 |  | Condensed phosphoric acid | pdf_6a8faacca882a39304796eef402a5436_2f87fc887af6b9a9f08ad5ddf0ab20ed7410596022594182 |
| PPB | PHOSPHORUS, BLACK | 黑磷 |  |  | pdf_6a8faacca882a39304796eef402a5436_fd6b27ac2994681276d9e4bf6e0ee9eb7410596022594182 |
| PPD | PROPANEDINITRILE | 丙二腈 | 109-77-3 | CyanacetonitrileDieyanomethaneMalonic distrileMalononitrileMethylene cyanide | pdf_6a8faacca882a39304796eef402a5436_93cb7cfc9a6b4d54a0f2039a227b76677410596022594182 |
| PPE | N-PENTYL PROPIONATE | 丙酸正戊酯 | 624-54-4 | n-Amyl propionate | pdf_6a8faacca882a39304796eef402a5436_2e4ce062acdae0510666464e33fc9b737410596022594182 |
| PPG | PROPYLENE GLYCOL | 丙二醇 | 57-55-6 | 1.2-DihydroxpropaneMethylethylene glycol1.2-Propanediol | pdf_6a8faacca882a39304796eef402a5436_a83508b782edd47a44a6261113ad1ccb7410596022594182 |
| PPI | POLYMETHYLENE POLYPHENYL ISOCYANATE | 多亚甲基多苯基异氰酸酯（PAPI） |  | PAPI | pdf_6a8faacca882a39304796eef402a5436_d40f112c6c2f7544cdf3609a9570b1907410596022594182 |
| PPL | PROPYLENE | 丙烯 | 115-07-1 | MethylethylenePropene | pdf_6a8faacca882a39304796eef402a5436_28e50c8efc491e0526fe0f5ccfbafabe7410596022594182 |
| PPO | PHOSPHORUS OXYCHLORIDE | 三氯氧磷 | 10025-87-3 | Phosphory chloride | pdf_6a8faacca882a39304796eef402a5436_0fb0f9448a5c1cabf7dc31685873eae27410596022594182 |
| PPP | PHOSPHORUS PENTASULFIDE | 五硫化二磷 | 1314-80-3 | Phosphoric sulfidePhosphoric persulfideThiophosphoric anhydride | pdf_6a8faacca882a39304796eef402a5436_53ee1f656e90014575ec4f447862c9707410596022594182 |
| PPR | PHOSPHORUS, RED | 红磷 |  | Amorphous phosphorus | pdf_6a8faacca882a39304796eef402a5436_a70fccd9a1a41e748ad0da294fb280247410596022594182 |
| PPT | PHOSPHORUS TRICHLORIDE | 三氯化磷 | 7719-12-2 |  | pdf_6a8faacca882a39304796eef402a5436_3fc1bbcecc14e28eaeea20244909947a7410596022594182 |
| PPW | PHOSPHORUS, WHITE | 白磷（黄磷） | 100320-09-0 | Yellow phosphorus | pdf_6a8faacca882a39304796eef402a5436_993ab86ecb55fd2d1823dcdc673572d27410596022594182 |
| PPZ | PIPERAZINE | 哌嗪 | 110-85-0 |  | pdf_6a8faacca882a39304796eef402a5436_f2c10e543644034c82328c82b89bbdde7410596022594182 |
| PRA | N-PROPYLAMINE | 正丙胺 |  | 1-AminopropameMono-n-propylamine1-Propylamine | pdf_6a8faacca882a39304796eef402a5436_5d9d300c6f9f2e3c2c1666b9d5cf14527410596022594182 |
| PRC | N-PROPYL CHLORIDE | 正丙基氯（1-氯丙烷） | 540-54-5 | 1-ChloropropanePropane, chloro- | pdf_6a8faacca882a39304796eef402a5436_d61790795a6adf464e579941028dd4647410596022594182 |
| PRD | PYRIDINE | 吡啶 | 110-86-1 |  | pdf_6a8faacca882a39304796eef402a5436_f8ef687f2bb00ff63a332142d4531abc7410596022594182 |
| PRE | N-PROPYL ETHER | 正丙醚 | 111-43-3 | Di-propyl etherDi-propyl ether | pdf_6a8faacca882a39304796eef402a5436_91c39a924127be82d160c2e95e5e95117410596022594182 |
| PRG | PROPARGITE | 炔螨特 | 2312-35-8 |  | pdf_6a8faacca882a39304796eef402a5436_c0c45cea07a5f23ac00390f9003a753d7410596022594182 |
| PRO | PROPARGYL ALCOHOL | 炔丙醇 | 107-19-7 |  | pdf_6a8faacca882a39304796eef402a5436_4da22de10577ff68589ce9be51b7f4237410596022594182 |
| PRP | PROPANE | 丙烷 | 74-98-6 | Dimethylmethane | pdf_6a8faacca882a39304796eef402a5436_030753c177e7d53f778c066f037cac5e7410596022594182 |
| PRR | PYRETHRINS | 除虫菊酯 | 8003-34-7 | Dalamation-insect powderPyrian-insect powderPyyrthriumflowers | pdf_6a8faacca882a39304796eef402a5436_3f5588b3fb53fb9ef013ae368c1580187410596022594182 |
| PTA | PENTANE | 戊烷 | 109-66-0 |  | pdf_6a8faacca882a39304796eef402a5436_f8b70a6383d444ad2882e4f2d5c14f107410596022594182 |
| PTB | PENTABORANE | 五硼烷 | 65580-80-5 | (9)-Pentaboron nonahydride | pdf_6a8faacca882a39304796eef402a5436_a0b54d441d89b58d06557755d1b123e27410596022594182 |
| PTC | POTASSIUM CYANIDE | 氰化钾 | 151-50-8 | Cyanide | pdf_6a8faacca882a39304796eef402a5436_dcccdcb306b48fba5f743575578b0e867410596022594182 |
| PTD | POTASSIUM DICROMATE | 重铬酸钾 |  | BichromePotassium bichromate | pdf_6a8faacca882a39304796eef402a5436_8d6b1b9892ab0b85ab6530b8f36fd6e77410596022594182 |
| PTE | 1-PENTENE | 1-戊烯 | 109-67-1 | alpha-n-AmylenePropylethylene | pdf_6a8faacca882a39304796eef402a5436_ace8ba3c01836b37343ff2157636f76a7410596022594182 |
| PTH | POTASSIUM HYDROXIDE | 氢氧化钾 | 1310-58-3 | Caustic potashLye | pdf_6a8faacca882a39304796eef402a5436_a7edc9d16f9d5f7ebde7d55a483c20a77410596022594182 |
| PTI | POTASSIUM IODIDE | 碘化钾 | 7681-11-0 |  | pdf_6a8faacca882a39304796eef402a5436_109563f7e1e1e1a8dc336c8d29bf23167410596022594182 |
| PTL | PETROLATUM | 凡士林 |  |  | pdf_6a8faacca882a39304796eef402a5436_9431b1d216b75338d73a74114148f6ed7410596022594182 |
| PTM | POTASSIUM | 钾 | 7440-09-7 | Potassium oxalate | pdf_6a8faacca882a39304796eef402a5436_28e5ebca0fec968b22d11c9a39553e377410596022594182 |
| PTN | PETROLEUM NAPHTHA | 石油石脑油 |  | Petroleum solvent | pdf_6a8faacca882a39304796eef402a5436_18b1e8059a51324d7846d715015e82a97410596022594182 |
| PTO | PARATHION | 对硫磷 | 56-38-2 | O,O-Diethyl O(p-nitrophenyl)phosphorothoateEthyl parathionPhosphorothoic acid, O | pdf_6a8faacca882a39304796eef402a5436_aa2dd231efd8842cb66e5cbc9bdf60017410596022594182 |
| PTP | POTASSIUM PERMANGANATE | 高锰酸钾 | 7722-64-7 |  | pdf_6a8faacca882a39304796eef402a5436_ae1c45e96bd0cd549d75f5848be4aadb7410596022594182 |
| PTR | NONENE | 壬烯 | 124-11-8 | Nonene (nonlinearPropylene trimerTripropylene | pdf_6a8faacca882a39304796eef402a5436_24834b501cf0d9e8c13e0b12dfdaa9a27410596022594182 |
| PTS | POTASSIUM OXALATE | 草酸钾 | 583-52-8 | Potassium oxalate monohyrate | pdf_6a8faacca882a39304796eef402a5436_5017070c0baab968aee8b08f32726d4f7410596022594182 |
| PTT | PROPYLENE TETRAMER | 丙烯四聚体 | 6842-15-5 | Dodecene (non-linear)Tetrapropylene | pdf_6a8faacca882a39304796eef402a5436_cb0ff77fa02fd156d7659532eee2c3477410596022594182 |
| PXE | 1-PHENYL-1-XYLYL ETHANE | 1-苯基-1-二甲苯基乙烷 |  | Hatcol XPEPhenyl xylyl ethane | pdf_6a8faacca882a39304796eef402a5436_3f67c950006d6e4c1825a385008a04347410596022594182 |
| PXP | N-PROPOXYPROPANOL | 正丙氧基丙醇 | 4161-22-2 |  | pdf_6a8faacca882a39304796eef402a5436_afb7347ed2dac37cfc31ed1063f9c16a7410596022594182 |
| QNL | QUINOLINE | 喹啉 | 91-22-5 | 1-Azanphthalene1-BenzazineBenzo (b) pyridineChinolineLeucol | pdf_6a8faacca882a39304796eef402a5436_38b581830bf2173a4ea830a12692404f7410596022594182 |
| RSC | RESORCINOL | 间苯二酚 | 108-46-3 | 1.3-Benzenediol1.3-Dihydroxybenzenem-DihydroxybenzeneDihydroxybenzenzResorcin | pdf_6a8faacca882a39304796eef402a5436_b4e5520520d56753a33782a12efbe6657410596022594182 |
| SAB | SODIUM ALKYLBENZENESULFONATES | 烷基苯磺酸钠 |  | Alky/benzeneusulfonic acid,sodium saltSuffonated alkylbenzene,sodium salt | pdf_6a8faacca882a39304796eef402a5436_73acfedaeed748223e468ae599ea67a17410596022594182 |
| SAC | SULFURIC ACID, SPENT | 废硫酸 | 7664-93-9 | Dilute sulfuric acid | pdf_6a8faacca882a39304796eef402a5436_b29db9a9ce4fa3b23450ae769de696ba7410596022594182 |
| SAL | SALICYLALDEHYDE | 水杨醛 | 90-02-8 | 2-Formyl phenolO-HydroxybenzaldehydeSalicylalSalicylical aldehyde | pdf_6a8faacca882a39304796eef402a5436_a0529b86360c017a0d7a1d4d90ac79487410596022594182 |
| SAM | SODIUM AMIDE | 氨基钠 | 7782-92-5 | Sodamide | pdf_6a8faacca882a39304796eef402a5436_fcd76de94180b62d850bbfc85b8d37127410596022594182 |
| SAR | SODIUM ARSENITE | 亚砷酸钠 | 7784-46-5 | Sodium meta arseniteSodium ortho arsenite | pdf_6a8faacca882a39304796eef402a5436_6cf6bd95322ab9b0bf2a84347d9a93927410596022594182 |
| SAS | SODIUM ALKYL SULFATES | 烷基硫酸钠 |  | Sodium hydrogen alkyl sulfate | pdf_6a8faacca882a39304796eef402a5436_ae923509580efbb49f1f8acf004faaaa7410596022594182 |
| SAT | SODIUM FLUOROACETATE | 氟乙酸钠 | 62-74-8 | Acetic acid, fluoro, sodium saltCompound 1080Fluoracetic acid, sodium saltSodium | pdf_6a8faacca882a39304796eef402a5436_89ec189ba6534c4ba73cab8dfb0274747410596022594182 |
| SAU | SODIUM ALUMINATE SOLUTION (45% OR LESS) | 铝酸钠溶液（≤45%） | 1302-42-7 |  | pdf_6a8faacca882a39304796eef402a5436_54fae2c2f8e749e4b1583793cc65c5227410596022594182 |
| SAZ | SODIUM AZIDE | 叠氮化钠 | 26628-22-8 | Hydrozaic acid, sodium salt | pdf_6a8faacca882a39304796eef402a5436_f7edc2990f673f11dddd644890da41cc7410596022594182 |
| SBF | SODIUM BIFLUORIDE | 氟化氢钠 | 1333-83-1 | Sodium difluorideSodium hydrogen difluorideSodium hydrogen fluoride | pdf_6a8faacca882a39304796eef402a5436_4c72cbd499e3c103cc01193bffa17a4d7410596022594182 |
| SBH | SODIUM BOROHYDRIDE | 硼氢化钠 | 16940-66-2 | Borohydride | pdf_6a8faacca882a39304796eef402a5436_787f18184c27af9cd07e32b6207dcca07410596022594182 |
| SBS | SODIUM BISULFITE | 亚硫酸氢钠 | 7631-90-5 | Sodium acid suffiteSodium metabissuffieSodium pyrosulifite | pdf_6a8faacca882a39304796eef402a5436_3be0495d2ca43b423f5887dab579f1b27410596022594182 |
| SBT | SORBITOL | 山梨醇 | 50-70-4 | D-GlusitolHexahydric alcohol1,2,3,4,5,6-HexanhexolSorbitSorbit | pdf_6a8faacca882a39304796eef402a5436_944b988cc6b67c24a408c03da20504f67410596022594182 |
| SBX | SODIUM HYDROXIDE SOLUTION | 氢氧化钠溶液 | 1310-73-2 |  | pdf_6a8faacca882a39304796eef402a5436_0e23914eaf117316ad592524bd5eb4a17410596022594182 |
| SCD | SODIUM CACODYLATE | 二甲胂酸钠 | 124-65-2 |  | pdf_6a8faacca882a39304796eef402a5436_2acd174b6f65183fa8af25623a7a0c0d7410596022594182 |
| SCH | SODIUM CHROMATE | 铬酸钠 | 7775-11-3 | Neutral sodium chromate anhydrousSodium chromate (VI) | pdf_6a8faacca882a39304796eef402a5436_8a6cec578110b3a64d1ec774ffe092dc7410596022594182 |
| SCL | SULFURYL CHLORIDE | 硫酰氯 | 7791-25-5 |  | pdf_6a8faacca882a39304796eef402a5436_40c4413747b8360dae37f576c793fece7410596022594182 |
| SCM | STRONTIUM CHROMATE | 铬酸锶 | 7789-06-2 | Chronic acid, strontium salt(1:1)Deep lemon yellowStrontium yellow | pdf_6a8faacca882a39304796eef402a5436_47f0131c117ad125c1667e2b5fe3b2997410596022594182 |
| SCN | SODIUM CYANIDE | 氰化钠 | 143-33-9 | Hydroycanyic acid, sodium salt | pdf_6a8faacca882a39304796eef402a5436_e477b4b1c358797da5b0d0e0018cbb747410596022594182 |
| SCR | SODIUM DICHROMATE | 重铬酸钠 | 10588-01-9 | Sodium bichromate | pdf_6a8faacca882a39304796eef402a5436_df05109ef355f1801e58ddcf95f9e1b97410596022594182 |
| SCY | SODIUM THIOCYANATE | 硫氰酸钠 | 540-72-7 |  | pdf_6a8faacca882a39304796eef402a5436_14fa4fce6697303468bfc3a0a6a340e47410596022594182 |
| SDA | SODIUM ARSENATE | 砷酸钠 | 7631-89-2 |  | pdf_6a8faacca882a39304796eef402a5436_75d96eb8994d96e7a496073404d9272a7410596022594182 |
| SDB | SODIUM BORATE | 硼砂（硼酸钠） | 1303-96-4 | Borax, anhydrosSodium biborateSodium pyroborateSodium tetraborate, anhydrous | pdf_6a8faacca882a39304796eef402a5436_e56cf809361c5db12edfdaab2b4b9aa47410596022594182 |
| SDC | SODIUM CHLORATE | 氯酸钠 | 7775-09-9 |  | pdf_6a8faacca882a39304796eef402a5436_741436c679dc2ccc78cf4e538c0981637410596022594182 |
| SDD | SODIUM CHLORATE SOLUTION | 氯酸钠溶液 | 7775-09-9 | Chlorate of sodaSoda chloric acid, sodium salt | pdf_6a8faacca882a39304796eef402a5436_49c4610b74df59e87d7641cb2427f8207410596022594182 |
| SDF | SODIUM FLUORIDE | 氟化钠 | 7681-49-4 |  | pdf_6a8faacca882a39304796eef402a5436_b6b24dec1a4a6f837357c3cb542875f07410596022594182 |
| SDH | SODIUM HYDRIDE | 氢化钠 | 7646-69-7 |  | pdf_6a8faacca882a39304796eef402a5436_977e68bae5e03d08c8f7403794feff687410596022594182 |
| SDN | SODIUM NITRATE | 硝酸钠 | 7631-99-4 | Chile salpeterNitrationSoda niter | pdf_6a8faacca882a39304796eef402a5436_c9fb0323c7aab1eccffa5cbf58c83d077410596022594182 |
| SDS | SODIUM SULFIDE | 硫化钠 | 1313-82-2 |  | pdf_6a8faacca882a39304796eef402a5436_bed19a7ebf6856bc346b1b5d445a5f837410596022594182 |
| SDT | SODIUM DICHLORO-S-TRIAZINETRIONE | 二氯异氰尿酸钠 | 2893-78-9 | Sodium dichorisoocyanurate | pdf_6a8faacca882a39304796eef402a5436_3184984d50087873f2cf5f2efa28281d7410596022594182 |
| SDU | SODIUM | 钠 | 7440-23-5 |  | pdf_6a8faacca882a39304796eef402a5436_2d6917b61c7c340e493a0454d560f78b7410596022594182 |
| SFA | SULFURIC ACID | 硫酸 | 7664-93-9 |  | pdf_6a8faacca882a39304796eef402a5436_1fabffa58c3e595093964fc2c8d7cde17410596022594182 |
| SFC | SODIUM FERROCYANIDE | 亚铁氰化钠 | 13601-19-9 |  | pdf_6a8faacca882a39304796eef402a5436_efe737b0ac0f43c4405446a287c56b0c7410596022594182 |
| SFD | SULFUR DIOXIDE | 二氧化硫 | 7446-09-5 |  | pdf_6a8faacca882a39304796eef402a5436_5cc7ce29702945ae10eb52645a1099397410596022594182 |
| SFL | SULFOLANE | 环丁砜 | 126-33-0 | Sulfolane-WTetrahydrothiophene-1,1-DioxideTetramethylene sulfone | pdf_6a8faacca882a39304796eef402a5436_046ca5bc92d2bd1bd3ca2243c6bce3c47410596022594182 |
| SFM | SULFUR MONOCHLORIDE | 一氯化硫 | 10025-67-9 |  | pdf_6a8faacca882a39304796eef402a5436_f27e1498cf786627a209bb0303e58e747410596022594182 |
| SFR | SODIUM SILICOFLUORIDE | 氟硅酸钠 | 16893-85-9 |  | pdf_6a8faacca882a39304796eef402a5436_88216fb2c8dd5c17e998b622afa704237410596022594182 |
| SHC | SODIUM HPOCHLORITE | 次氯酸钠 | 7681-52-9 | Liquid bleach | pdf_6a8faacca882a39304796eef402a5436_916fde4a0d99ae4df1def18d38d90fe57410596022594182 |
| SHD | SODIUM HYDROXIDE | 氢氧化钠 | 1310-73-2 | Caustic sodaLye | pdf_6a8faacca882a39304796eef402a5436_bb57497486a4090d18273c2cbe2ac74c7410596022594182 |
| SHP | SODIUM HPOCHLORITE SOLUTION | 次氯酸钠溶液 | 7681-52-9 |  | pdf_6a8faacca882a39304796eef402a5436_b8bd61d2444f2b672a1c2b01bc342ff67410596022594182 |
| SHR | SODIUM HYDROSULFIDE SOLUTION | 硫氢化钠溶液 | 16721-80-5 | SodiumbisulfideSodium hydrogen sulfideSodium sulfhydrate | pdf_6a8faacca882a39304796eef402a5436_2c35a2ec8a820a2fa6eb84a076f464de7410596022594182 |
| SHX | SODIUM HYDROGEN SULFITE SOLUTION (35% OR LESS) | 亚硫酸氢钠溶液（≤35%） | 7631-90-5 | Sodium bisulfite solution | pdf_6a8faacca882a39304796eef402a5436_6915b584123b3f67b26ed04978b22ba37410596022594182 |
| SLA | SALICYLIC ACID | 水杨酸 | 69-72-7 | o-Hydroxybenzo acid Retarder W | pdf_6a8faacca882a39304796eef402a5436_839fc0d940d47ebe76f4e9f6c7163b987410596022594182 |
| SLD | SELENIUM DIOXIDE | 二氧化硒 | 7446-08-4 | Selenious anhydrideSelenium oxide | pdf_6a8faacca882a39304796eef402a5436_1e5a5999902e11ba08c6ac71fe0870497410596022594182 |
| SMB | SODIUM 2-MERCAPTOBENZOTHIAZOL SOLUTION | 2-巯基苯并噻唑钠溶液 |  | 2-Benzothiazolethol, sodium salt2-(3h)-benzothiazolethol, sodium saltDudedexNaca | pdf_6a8faacca882a39304796eef402a5436_52bcdc34b5ba74d07b75b75afcc67bc47410596022594182 |
| SML | SODIUM METHYLATE | 甲醇钠 | 124-41-4 | Sodium methoxide | pdf_6a8faacca882a39304796eef402a5436_1d4ea5d71b1bd8805cf52c8a480cc05a7410596022594182 |
| SNI | SODIUM NITRITE SOLUTION | 亚硝酸钠溶液 | 7632-00-0 | Sodium nitrile | pdf_6a8faacca882a39304796eef402a5436_db9b568eef30f4f3ab08349ecbddac277410596022594182 |
| SNT | SODIUM NITRITE | 亚硝酸钠 | 7632-00-0 | EcrinitriFilmerine | pdf_6a8faacca882a39304796eef402a5436_d6aaf54432f81a25f7a61ce0ebc4ad387410596022594182 |
| SOX | SODIUM OXALATE | 草酸钠 | 62-76-0 | Ethanedioic acid, disodium salt | pdf_6a8faacca882a39304796eef402a5436_a351095c624586325f6a7da980549af57410596022594182 |
| SPC | SODIUM PENTACHLOROPHENATE | 五氯苯酚钠 | 131-52-2 | Phenol, pentachloro-, sodium salt | pdf_6a8faacca882a39304796eef402a5436_4cb68161c3a94f9c9e22c5f27c78bd987410596022594182 |
| SPH | SODIUM PHOSPHATE, TRIBASIC | 磷酸三钠 | 7601-54-9 |  | pdf_6a8faacca882a39304796eef402a5436_0066bc566524f473d9007c41656fd6357410596022594182 |
| SPP | SODIUM PHOSPHATE | 磷酸钠 |  |  | pdf_6a8faacca882a39304796eef402a5436_54af710b4cd8023a07cb6e4af6b410057410596022594182 |
| SRA | STEARIC ACID | 硬脂酸 | 57-11-4 | 1-Heptadecanecarboxylic acidOctadecanolic acidn-Octadecylic acidStearophanic aci | pdf_6a8faacca882a39304796eef402a5436_9dee6cf12c43ea98a90bee31328e054d7410596022594182 |
| SRS | SUCROSE | 蔗糖 | 57-50-1 |  | pdf_6a8faacca882a39304796eef402a5436_5c0cfa4670db92a787f9fde8d7582f4d7410596022594182 |
| SSC | SODIUM SILICATE | 硅酸钠（水玻璃） | 1344-09-8 | Soluble glassWater glass | pdf_6a8faacca882a39304796eef402a5436_0b967d9a1ee0d9cb25515d6cd595ef7f7410596022594182 |
| SSE | SODIUM SELENITE | 亚硒酸钠 | 10102-18-8 | Disodium selenteSelenious acid, disodium salt | pdf_6a8faacca882a39304796eef402a5436_f964071db6fe6ea3a60bb5d52cc20bb17410596022594182 |
| SSF | SODIUM SULFITE | 亚硫酸钠 | 7757-83-7 |  | pdf_6a8faacca882a39304796eef402a5436_467f9306b67531a1a66f905af7ec74f77410596022594182 |
| STC | SILICON TETRACHLORIDE | 四氯化硅 | 10026-04-7 | Silicon chloride | pdf_6a8faacca882a39304796eef402a5436_86da2b9e94fbea71d1a5679bd6147ae47410596022594182 |
| STF | STANNOUS FLOURIDE | 氟化亚锡 | 7783-47-3 | FlouristanTin difliourideKeep people away.Wear goggles and self-contained respir | pdf_6a8faacca882a39304796eef402a5436_14151e89b5fbe91e86f0cb0d72dea59e7410596022594182 |
| STN | STRONTIUM NITRATE | 硝酸锶 | 10042-76-9 |  | pdf_6a8faacca882a39304796eef402a5436_3eb2879ebab62462f078decc3116d7647410596022594182 |
| STO | SELENIUM TRIOXIDE | 三氧化硒 | 13768-86-0 | Selenic anthdride | pdf_6a8faacca882a39304796eef402a5436_fafb429322b59f5767d0b0111892780d7410596022594182 |
| STR | STRYCHNINE | 士的宁 | 57-24-9 |  | pdf_6a8faacca882a39304796eef402a5436_bf566715513d2619e8c6dffcfad0b7ae7410596022594182 |
| STS | SODIUM THIOCYANATE SOLUTION (56% OR LESS) | 硫氰酸钠溶液（≤56%） | 540-72-7 |  | pdf_6a8faacca882a39304796eef402a5436_5f47b1d7670f5dd1a65c2c25660365e17410596022594182 |
| STY | STYRENE | 苯乙烯 | 100-42-5 | WheryletyleneStyrolStyroleneVinyl benzene | pdf_6a8faacca882a39304796eef402a5436_1fc6d5aaec026c5cf6c9a165c551eb817410596022594182 |
| SVA | SILVER ACETATE | 乙酸银 | 563-63-3 |  | pdf_6a8faacca882a39304796eef402a5436_2632ca03200343529d646edc00c3c0257410596022594182 |
| SVC | SILVER CARBONATEsvc | 碳酸银 |  |  | pdf_6a8faacca882a39304796eef402a5436_1f3fc2ae872ec86bb9cf615a463dad177410596022594182 |
| SVF | SILVER FLUORIDE | 氟化银 | 7775-41-9 |  | pdf_6a8faacca882a39304796eef402a5436_9f0c21770801162b787300ba38dc588e7410596022594182 |
| SVI | SILVER IODATE | 碘酸银 | 7783-97-3 |  | pdf_6a8faacca882a39304796eef402a5436_877877aceab93f5ed389bbf1d8e6a9217410596022594182 |
| SVN | SILVER NITRATE | 硝酸银 | 7761-88-8 | Lunar caustic | pdf_6a8faacca882a39304796eef402a5436_2d979a7d4445d08d36845a31e8bcc2037410596022594182 |
| SVO | SILVER OXIDEsvo | 氧化银 |  | Argentous oxide | pdf_6a8faacca882a39304796eef402a5436_1ca9eaf22005a9e485eb0cbdc0009a4e7410596022594182 |
| SVS | SILVER SULFATE | 硫酸银 | 10294-26-5 |  | pdf_6a8faacca882a39304796eef402a5436_fe165c3b30e9ec1c23552e10c574b9b47410596022594182 |
| SXX | SULFUR | 硫 | 7704-34-9 | Brimstone | pdf_6a8faacca882a39304796eef402a5436_142dcca3ebb33450d40780fef7862a3c7410596022594182 |
| TAA | TRIMETHYLACETIC ACID | 三甲基乙酸（特戊酸） | 75-98-9 | alpha, alpha-Dimethyl-proponicacidNeopentanoic acidPivallic acidPropanoic acid,  | pdf_6a8faacca882a39304796eef402a5436_9997cb217ccbf7f51e71b9664675b6827410596022594182 |
| TAL | TRIETHYLALUMINUM | 三乙基铝 | 97-93-8 | Aluminum triethylATETEA | pdf_6a8faacca882a39304796eef402a5436_940d5b2d9f9afc5275ec51278aed14f57410596022594182 |
| TAP | P-TOLUENESULFONIC ACID | 对甲苯磺酸 | 104-15-4 | Methylbenzenesufonic acidTosic acidp-TSA | pdf_6a8faacca882a39304796eef402a5436_8700228df5b51b584885fd8ca62e5dab7410596022594182 |
| TAS | 2,4,5-TRICHLOROPHENOXYACETIC ACID, SODIUM SALT | 2,4,5-三氯苯氧乙酸钠（2,4,5-T钠盐） |  | 2,4,5-T sodium salt | pdf_6a8faacca882a39304796eef402a5436_d878e5f87481198ff0a54362b73a5abc7410596022594182 |
| TBP | TRIBUTYL PHOSPHATE | 磷酸三丁酯（TBP） | 126-73-8 | Phosphoric acid, tri-butyl esterTBPTri-n-butyl phosphate | pdf_6a8faacca882a39304796eef402a5436_ddc9a18c32e34ab3d81a4d3d87a2c7c67410596022594182 |
| TBT | TETRABUTYL TITANATE | 钛酸四丁酯 | 5593-70-4 |  | pdf_6a8faacca882a39304796eef402a5436_524d9b9c5177c81fe78fa92912fe0f257410596022594182 |
| TBZ | 1,2,3-TRICHLOROBENZENE | 1,2,3-三氯苯 | 87-61-6 | Benzene, 1,2-3trichioro-Pyanol 1478V-TrichlorobenzeneVic-Trichlorobenzene | pdf_6a8faacca882a39304796eef402a5436_6adc45efdfe0bfb06b718484246c03b07410596022594182 |
| TCA | 2,4,5-TRICHLOROPHENOXYACETIC ACID | 2,4,5-三氯苯氧乙酸（2,4,5-T） | 93-76-5 | 2,4,5-T | pdf_6a8faacca882a39304796eef402a5436_0326faab2bcad74515f6f69b7b6cbb9e7410596022594182 |
| TCB | 1,2,4-TRICHLOROBENZENE | 1,2,4-三氯苯 | 120-82-1 | Benzene, 1,2,4-trichloro-unsym-Trichlorobenzene1,2,4-Trichlorobenzol | pdf_6a8faacca882a39304796eef402a5436_2955fbf6169c9692964c20b03635c7977410596022594182 |
| TCE | TRICHLOROETHANE | 三氯乙烷 | 71-55-6 |  | pdf_6a8faacca882a39304796eef402a5436_5ec7b25654cb99bd038371f34eaf1dd27410596022594182 |
| TCF | TRICHLOROFLUOROMETHANE | 三氯氟甲烷 | 75-69-4 |  | pdf_6a8faacca882a39304796eef402a5436_b72104ef5843ce0f0f33b64f96512fa97410596022594182 |
| TCH | TRICHLOROACETALDEHYDE | 三氯乙醛（氯醛） | 75-87-6 |  | pdf_6a8faacca882a39304796eef402a5436_f69fc692fc208b0ff9856f8bbfc5f7c27410596022594182 |
| TCL | TRICHLOROETHYLENE | 三氯乙烯 | 79-01-6 | ChölyenGemalgeneTrethyleneTrichloranTriclene algyenTrilene | pdf_6a8faacca882a39304796eef402a5436_6dc54443023f4826842c737797b77f517410596022594182 |
| TCM | 1,1,2-TRICHOROETHANE | 1,1,2-三氯乙烷 | 79-00-5 | Ethane, 1, 1,2-trichorobeta-trichorethaneVinyl trichloride | pdf_6a8faacca882a39304796eef402a5436_91a7025b82e6418460ff23d4ca7d16457410596022594182 |
| TCN | 1,2,3-TRICHLOROPROPANE | 1,2,3-三氯丙烷 | 96-18-4 |  | pdf_6a8faacca882a39304796eef402a5436_ad92cc69b2fd8a58247889c36ffc556e7410596022594182 |
| TCO | TRICRESYL PHOSPHATE (>= 1% ORTHO ISOMER) | 磷酸三甲苯酯（≥1%邻位） | 78-32-0 | o-CresyphosphatePhosphoric acid, trís(2-methylphenyl) estero-Tolylphosphate phos | pdf_6a8faacca882a39304796eef402a5436_a889e2c59b1c5a09e69e921fce180b287410596022594182 |
| TCP | TRICRESYL PHOSPHATE (<1% ORTHO ISOMER) | 磷酸三甲苯酯（<1%邻位） | 78-32-0 |  | pdf_6a8faacca882a39304796eef402a5436_e01dae34fd69518222a0c52d43db4ce97410596022594182 |
| TCS | TRICHLOROSILANE | 三氯硅烷 | 10025-78-2 | SilicochloroformTrichlormonosilane | pdf_6a8faacca882a39304796eef402a5436_a701363fb70af97b7ef6feef5f4487ff7410596022594182 |
| TCT | TRICHLORO-S-TRIAZINETRIONE | 三氯异氰尿酸 | 87-90-1 | Trichloroiminosocyanic acid Trichloroizocyanic acid Trichlorotrizainetion Trichl | pdf_6a8faacca882a39304796eef402a5436_d4697875ec647bec5bca15b81bbe61877410596022594182 |
| TDA | TOLUENEDIAMINE | 甲苯二胺 | 95-80-7 | 2.4-Diaminotoluene2.4-Tolamine2.4-Tolunediamimem-Toluene diaminemeta-Tolunediami | pdf_6a8faacca882a39304796eef402a5436_a6ffe146a15d328220660224478c2f217410596022594182 |
| TDB | TETRADECYLBENZENE | 十四烷基苯 | 1459-10-5 | 1-Phenytetradecane | pdf_6a8faacca882a39304796eef402a5436_93fbb88b478e7cd6a13175295c37f2777410596022594182 |
| TDC | 1-TRIDECENE | 1-十三烯 | 2437-56-1 | Undecylethylene | pdf_6a8faacca882a39304796eef402a5436_8590b0bf06cbee8ce12a74fcd201a0a17410596022594182 |
| TDI | TOLUENE 2,4-DIISOCYANATE | 甲苯2,4-二异氰酸酯（TDI） | 584-84-9 |  | pdf_6a8faacca882a39304796eef402a5436_077752494ba58ee98da6062d4588592a7410596022594182 |
| TDN | TRIDECANOL | 十三醇 | 112-70-9 |  | pdf_6a8faacca882a39304796eef402a5436_67dce0d9753ebfda11a1f8b8c8a5eaec7410596022594182 |
| TEA | TRIETHANOLAMINE | 三乙醇胺 | 102-71-6 | Tris(Hydroxyethyl)lamineTriethydroxytriethylamine | pdf_6a8faacca882a39304796eef402a5436_94b71465230972b48ec49987c33381c67410596022594182 |
| TEB | TRIETHYLBENZENE | 三乙苯 | 25340-18-5 | 1.3.5-Triethylbenzenesym-Triethylbenzene | pdf_6a8faacca882a39304796eef402a5436_12605348deaa06ad8c44ea0c4bd33cd17410596022594182 |
| TEC | TETRACHLOROETHANE | 四氯乙烷 | 79-34-5 | Acylene tetrachloride1,1,2,2-Tetrachloroethane | pdf_6a8faacca882a39304796eef402a5436_265ca2c012f12fb4656ff5faba8e36867410596022594182 |
| TED | TETRAETHYL DITHIOPYROPHOSPHATE | 二硫代焦磷酸四乙酯 | 3689-24-5 | Dithiopyrophosphoric acid,0,0,0,0-tetraethyl esterSulfotepTetraethyldithonopyrop | pdf_6a8faacca882a39304796eef402a5436_4173f7f2b6bbe68d49eceeb794c10dd57410596022594182 |
| TEG | TRIETHYLENE GLYCOL | 三甘醇 | 112-27-6 | Di-beta-hydroxyethane2.2&#x27 -EthylenedoxydethanolEthylene glycol dihydroxydiet | pdf_6a8faacca882a39304796eef402a5436_70d40bba6154845ce48d15dfda909e297410596022594182 |
| TEL | TETRAETHYL LEAD | 四乙基铅 | 78-00-2 | Lead tetraethylTEL | pdf_6a8faacca882a39304796eef402a5436_67126101de63b01c99cc85bc0efbe1ac7410596022594182 |
| TEN | TRIETHYLAMINE | 三乙胺 | 121-44-8 | TEN | pdf_6a8faacca882a39304796eef402a5436_36aa69b1b0b11c477a7000c9ca7c72337410596022594182 |
| TEP | TETRAETHYL PYROPHOSPHATE | 焦磷酸四乙酯（TEPP） | 107-49-3 |  | pdf_6a8faacca882a39304796eef402a5436_582a891ec836cf2a759d75e02602216f7410596022594182 |
| TES | 2,4,5-T ESTERS | 2,4,5-T酯类 |  |  | pdf_6a8faacca882a39304796eef402a5436_bc9fac008f07a23de8331ac622ab4ba07410596022594182 |
| TET | TRIETHYLENETETRAMINE | 三乙烯四胺 | 112-24-3 | N.N-bis-(2.-Aminoethyl)ethylenediamineTETATrien | pdf_6a8faacca882a39304796eef402a5436_871b0d386703b36c13c4747591b9c9707410596022594182 |
| TFA | TALLOW FATTY ALCOHOL | 牛油脂肪酸醇 |  | Higher fatty alcoholStearyl alcohol, crude | pdf_6a8faacca882a39304796eef402a5436_1be34ef6fc8a033a06c0c4ef2826329e7410596022594182 |
| TFC | TRIFLUOROCHLOROETHYLENE | 三氟氯乙烯 | 79-38-9 | ChlorotrifluocethyleneCTFEGenetron 1113Kel F monomerTrifluomonochloroethyleneTri | pdf_6a8faacca882a39304796eef402a5436_7674f004d2157e641ea42142253c9b9b7410596022594182 |
| TFE | TETRAFLUOROETHYLENE | 四氟乙烯 | 116-14-3 | Teflon monomer | pdf_6a8faacca882a39304796eef402a5436_57abfbe7b176ca185ab5ef1d3118d0057410596022594182 |
| TFR | TRIFLURALIN | 氟乐灵 | 1582-09-8 | 2.6-Dnitro-n,n-dipropyl-4-trifluomethylanilineTreflanalpha,alpha,alpha-Trifluoro | pdf_6a8faacca882a39304796eef402a5436_1a23671a0ae8ec0478eb2d950b9ed1877410596022594182 |
| TGC | TRIPROPYLENE GLYCOL | 三丙二醇 |  |  | pdf_6a8faacca882a39304796eef402a5436_066c57973def9a03bd3086b82de086487410596022594182 |
| TGD | TRIETHYLENE GLYCOL DI-(2-ETHYLBUTYRATE) | 三甘醇二（2-乙基丁酸）酯 | 95-08-9 | Triglycol dicaproateTriglycol dihexoate | pdf_6a8faacca882a39304796eef402a5436_549f465a26461b41591c40e2e477c3e67410596022594182 |
| TGE | TRIETHYLENE GLYCOL ETHYL ETHER | 三甘醇乙醚 | 112-50-5 | Triethylene glycol monoethyletherTriglycol monoethyl ether | pdf_6a8faacca882a39304796eef402a5436_93853a1492d1ca83084b9d49afc9eafe7410596022594182 |
| TGM | TRIPROPYLENE GLYCOL METHYL ETHER | 三丙二醇甲醚 | 10213-77-1 | Dowanol TPMPropanol, 3-(3-(3-methoxypropoxy)- | pdf_6a8faacca882a39304796eef402a5436_cee5603050251344336bbf5515693e487410596022594182 |
| TGY | TRIETHYLENE GLYCOL METHYL ETHER | 三甘醇甲醚 | 112-35-6 | Triethylene glycol monomethyletherTriglycol methyl ether | pdf_6a8faacca882a39304796eef402a5436_9fd6a26c881a1a5d1ee243ee5a1687897410596022594182 |
| THA | TRIMETHYL HEXAMETHYLENE DIAMINE | 三甲基六亚甲基二胺 |  | 1.6-Diamino-2.2.4(or 2.4,4)-trimethylhexane1.6-Hexanediamine,2.2,4(or 2,4,4)-tri | pdf_6a8faacca882a39304796eef402a5436_777073c49fc86fda6e0b93fc23fb73fc7410596022594182 |
| THB | THALLIUM CARBONATE | 碳酸铊 | 6533-73-9 |  | pdf_6a8faacca882a39304796eef402a5436_8ae0eddbf40779e95a49b853b34f5ce47410596022594182 |
| THC | THIOCARBAMIDE | 硫脲 | 62-56-6 |  | pdf_6a8faacca882a39304796eef402a5436_628f503e01cff7cb754a17ac81a6240b7410596022594182 |
| THF | TETRAHYDROFURAN | 四氢呋喃（THF） | 109-99-9 | Diethylene oxideTetramethylene oxideTHF | pdf_6a8faacca882a39304796eef402a5436_24337aa25bc6a5be1cc01445309b4be67410596022594182 |
| THI | TRIMETHYLHEXAMETHYLENE DIISOCYANATE | 三甲基六亚甲基二异氰酸酯（TMDI） | 28679-16-5 | Hexane, 1,6-dilisocyanato-2,2,4(2,4,-trimethyl- | pdf_6a8faacca882a39304796eef402a5436_59672d03e16c556e9d5329dbf5dabd8a7410596022594182 |
| THM | TETRANITROMETHANE | 四硝基甲烷 | 509-14-8 | NC1-C55947TetanTNM | pdf_6a8faacca882a39304796eef402a5436_6af3827154b40279b924d714dc7ac4897410596022594182 |
| THN | TETRAHYDRONAPHTHALENE | 四氢化萘（萘满） | 119-64-2 | 1.2.3.4-TetrahydronaphthaleneTetrainTetrampTetranap | pdf_6a8faacca882a39304796eef402a5436_c8f0859af2766b67de6b7b9b4a394c787410596022594182 |
| THR | THIRAM | 福美双 | 137-26-8 |  | pdf_6a8faacca882a39304796eef402a5436_b3aa59104c3429ffd78586e6dfe360d17410596022594182 |
| TIA | TRIISOBUTYLALUMINUM | 三异丁基铝 | 100-99-2 | Aluminum trisobutylTIBATibal | pdf_6a8faacca882a39304796eef402a5436_15d275339c3d03d913cfec245aab5b5c7410596022594182 |
| TIB | TRIISOBUTYLENE | 三异丁烯 | 39761-68-7 | Isobutene trimer1-Propene, 2-methyl trimerTrisobuteneUN 2324 (DOT) | pdf_6a8faacca882a39304796eef402a5436_300cb499d34ba7086ce82cdf5b5d373d7410596022594182 |
| TIP | TRIISOPROPANOLAMINE | 三异丙醇胺 | 122-20-3 | Tris(2-Hydroxpropyl) amine2-Propanol 1,1&#x27 1&#x27 -ntrilotri-Tri-Iso-propanol | pdf_6a8faacca882a39304796eef402a5436_3fb4a1a635bad4eea66b0280d2ae18557410596022594182 |
| TLA | THALLIUM ACETATE | 乙酸铊 | 563-68-8 | Acetic acid, thallum (1) saltAcetic acid, thallum saltThallum (1) acetateThallum | pdf_6a8faacca882a39304796eef402a5436_ccdffeb730ef234d963895b394b901e17410596022594182 |
| TLI | O-TOLUIDINE | 邻甲苯胺 | 95-53-4 | 2-Amino-1-methylbenzene2-Aminotoluene2-Methylanilineo-Methylanilineo | pdf_6a8faacca882a39304796eef402a5436_91e281091ce3472e565af483a456368b7410596022594182 |
| TLO | TALLOW | 牛油 |  | Edible tallowInedible tallowTallow oil | pdf_6a8faacca882a39304796eef402a5436_230f5f77269876f8cfac4d53294602457410596022594182 |
| TMA | TRIMETHYLAMINE | 三甲胺 | 75-50-3 |  | pdf_6a8faacca882a39304796eef402a5436_80bf70da924af118d2d002934241db447410596022594182 |
| TMC | TRIMETHYLCHLOROSILANE | 三甲基氯硅烷 | 75-77-4 | ChlorotrimethylisylineTrimethylsilyl chloride | pdf_6a8faacca882a39304796eef402a5436_73f9a51d7c4dc8a906ccf3fe20005edc7410596022594182 |
| TME | 1,2,4-TRIMETHYLBENZENE | 1,2,4-三甲苯 | 95-63-6 |  | pdf_6a8faacca882a39304796eef402a5436_5e6eb0d2d8c715bea24ea63db396b2937410596022594182 |
| TML | TETRAMETHYL LEAD | 四甲基铅 | 75-74-1 | Lead tetramethyl | pdf_6a8faacca882a39304796eef402a5436_26339bc2d3f14ce0d7f7682d8140ff777410596022594182 |
| TMP | 1-ISOBUTYRATE | 1-异丁酸酯 |  |  | pdf_6a8faacca882a39304796eef402a5436_752ed533c40bd475a25a49ed76813b0d7410596022594182 |
| TNA | TANNIC ACID | 鞣酸（单宁酸） | 5424-20-4 |  | pdf_6a8faacca882a39304796eef402a5436_e419d72b6842664560722cd7754c271c7410596022594182 |
| TNI | THALLIUM NITRATE | 硝酸铊 | 10102-45-1 | Nitric acid, thallous saltThallum monontrateThallum (1) nitrateThallous nitrate | pdf_6a8faacca882a39304796eef402a5436_abe4818de6fbd7fcb6d7b32ccacc82ff7410596022594182 |
| TNM | TETRANITROMETHANE | 四硝基甲烷 | 509-14-8 | NC1-C55947TetanTNM | pdf_6a8faacca882a39304796eef402a5436_ac516600578b01ec66b2ec1234d697cc7410596022594182 |
| TOD | P-TOLUIDINE | 对甲苯胺 | 106-49-0 | 4-Amino-1-methylbenzene4-Aminololubane4-Methylanilinep-Methylaniline4-Methylbenz | pdf_6a8faacca882a39304796eef402a5436_2809ed94152813d3aec4a127dba925767410596022594182 |
| TOF | TALL OIL, FATTY ACID | 妥尔油脂肪酸 |  | Tall oil fatty oil | pdf_6a8faacca882a39304796eef402a5436_e645505fa775a4c3290303bbfab1ec5f7410596022594182 |
| TOI | M-TOLUIDINE | 间甲苯胺 | 108-44-1 | 3-Amino-1-methylbenzene3-Amino-1-eneurene3-Methylanilinem-Methylaniline3-Methylb | pdf_6a8faacca882a39304796eef402a5436_56753d3d9983c8972b684904296ffb1c7410596022594182 |
| TOL | TOLUENE | 甲苯 | 108-88-3 | MethylbenzeneMethylbenzolToluol | pdf_6a8faacca882a39304796eef402a5436_9583f4f5bc7b8af593e3700aa81fc6937410596022594182 |
| TPA | 2-(2,4,5-TRICHLOROPHENOXY) PROPANOIC ACID | 2-(2,4,5-三氯苯氧基)丙酸 |  |  | pdf_6a8faacca882a39304796eef402a5436_773aa2dc049531404163c2a88c23f52c7410596022594182 |
| TPE | ISOOCTYL ESTER | 异辛酯 |  | Silvex, isoctyl ester2,4,5-TP acid esters | pdf_6a8faacca882a39304796eef402a5436_8ef4ebb1ab040a598dd5e8576a69b3ac7410596022594182 |
| TPG | THIOPHOSGENE | 硫代光气 | 463-71-8 | Thiocarbony/chloride | pdf_6a8faacca882a39304796eef402a5436_bbcd89eae66aa37f811b01b3e4726db57410596022594182 |
| TPH | TRICHLOROPHENOL | 三氯苯酚 | 15950-66-0 | Dowicide 2OnalPhanachtor2,4,5-Trichlorophenol | pdf_6a8faacca882a39304796eef402a5436_b9048c9c18d2404b8cdb8a8ace4670447410596022594182 |
| TPI | TRIETHYL PHOSPHITE | 亚磷酸三乙酯 | 122-52-1 | Phosphorous acid, triethyl esterUN 2323 (DOT) | pdf_6a8faacca882a39304796eef402a5436_8dc0f31df650779cda9fecb3ecbdd1db7410596022594182 |
| TPO | TRIS(AZIRIDINYL)PHOSPHINE OXIDE | 三（氮丙啶基）氧化膦 | 545-55-1 | APOTris(1-Aziridinyl) phosphineoxidePhosphoric acidtriethyleneimideTriethyleneph | pdf_6a8faacca882a39304796eef402a5436_5b9a4f42f59c71cf20084e8a130f9d347410596022594182 |
| TPP | TRIMETHYL PHOSPHITE | 亚磷酸三甲酯 | 121-45-9 | Methyl PhosphitePhosphorous acidTMPTrimethyl ester | pdf_6a8faacca882a39304796eef402a5436_345d231875df2e603522adbe60bb1c877410596022594182 |
| TPS | TRIETHYL PHOSPHATE | 磷酸三乙酯 | 78-40-0 |  | pdf_6a8faacca882a39304796eef402a5436_0d34e70b8625fbc296d179dc190e80267410596022594182 |
| TPT | TURPENTINE | 松节油 |  |  | pdf_6a8faacca882a39304796eef402a5436_40fc99ee0f642e1d3834d4392242b1fc7410596022594182 |
| TRB | TRIDECYLBENZENE | 十三烷基苯 | 123-02-4 | 1-Phenytridecane | pdf_6a8faacca882a39304796eef402a5436_8c890179df840804621d7606cecf479a7410596022594182 |
| TRC | TRICHLORFON | 敌百虫 | 52-68-6 |  | pdf_6a8faacca882a39304796eef402a5436_44e396774d7379107dde549ae2a889de7410596022594182 |
| TRD | TRIDECANE | 十三烷 | 629-50-5 | n-Tridecane | pdf_6a8faacca882a39304796eef402a5436_d48565c33aaf4a80add399cf130506317410596022594182 |
| TRL | TRIPROPYLAMINE | 三丙胺 | 102-69-2 | Tri-n-propylamine | pdf_6a8faacca882a39304796eef402a5436_eb79abb7186cae15b3f542be5fc981c87410596022594182 |
| TRN | THORIUM NITRATE | 硝酸钍 | 13823-29-5 | Thorium nitrate tetrahydrate | pdf_6a8faacca882a39304796eef402a5436_f2be9f9deb1ceb9d282d4c89e70123bf7410596022594182 |
| TRP | TRIXYLENYL PHOSPHATE | 磷酸三二甲苯酯 | 25155-23-1 | Cosilite NTPDimethylphenol phosphate (3:1)Reofos 95Tridimethylphenyl phosphateTr | pdf_6a8faacca882a39304796eef402a5436_c0c2e93f632e6e4169adc2a8b5ee7e1e7410596022594182 |
| TSU | THALLIUM SULFATE | 硫酸铊 | 7446-18-6 |  | pdf_6a8faacca882a39304796eef402a5436_dddfe3c4816caa8296e8ff6122c4da907410596022594182 |
| TTB | 1,2,3,5-TETRAMETHYLBENZENE | 1,2,3,5-四甲苯 | 527-53-7 | Isodurene | pdf_6a8faacca882a39304796eef402a5436_71682c0e2dbd68beaa35a12c673c048e7410596022594182 |
| TTD | 1-TETRADECENE | 1-十四烯 | 1120-36-1 | Dodecyletylene | pdf_6a8faacca882a39304796eef402a5436_16f08843d102cb1bed417b458e15ae887410596022594182 |
| TTE | TETRACHLOROETHYLENE | 四氯乙烯 | 127-18-4 | PerchloroethylenePerclenePerkPerkTetrap | pdf_6a8faacca882a39304796eef402a5436_730cde93f5bbd3503183e0358e7357787410596022594182 |
| TTF | 2020. 11. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 2021. 202 | （英文名OCR损坏） |  |  | pdf_6a8faacca882a39304796eef402a5436_2585d974124c50307fa8ef0bca0679917410596022594182 |
| TTG | TETRAETHYLENE GLYCOL | 四甘醇 | 112-60-7 |  | pdf_6a8faacca882a39304796eef402a5436_d07377d7e06e2d951f3b0b5f8088f5ff7410596022594182 |
| TTN | TETRADECANOL | 十四醇 | 112-72-1 |  | pdf_6a8faacca882a39304796eef402a5436_62c82aa73db86cef0b3998d06354c3487410596022594182 |
| TTP | TETRAETHYLENEPENTAMINE | 四乙烯五胺 | 112-57-2 | 1,11-Diamino-3,6,9-triazaundecane | pdf_6a8faacca882a39304796eef402a5436_b32310cfecb14f0b4e05d77f635d2d697410596022594182 |
| TTT | TITANIUM TETRACHLORIDE | 四氯化钛 | 7550-45-0 |  | pdf_6a8faacca882a39304796eef402a5436_4a73435fc54d9a4a0a76104af382d7497410596022594182 |
| TXP | TOXAPHENE | 毒杀芬 | 8001-35-2 | Octachlorocamphene | pdf_6a8faacca882a39304796eef402a5436_1068543ae8da3b3df8ba53138d8ffb1b7410596022594182 |
| UAN | URANYL NITRATE | 硝酸铀酰 | 10102-06-4 | Uranium nitrate | pdf_6a8faacca882a39304796eef402a5436_6873f20a319701b317b052f8d79b39fd7410596022594182 |
| UAS | UREA, AMMONIUM NITRATE SOLN (W/AQUA AMMONIA) | 尿素-硝酸铵溶液（含氨水） |  | Liquamon 28Uran, rustica | pdf_6a8faacca882a39304796eef402a5436_af6e13478dced9b0a30efa7d1d39a5707410596022594182 |
| UDA | UNDECANOIC ACID | 十一烷酸 | 112-37-8 | 1-Decanecarboxylic acidHendecanoic acidn-Undecanoic acidn-Undecoic acidn-Undecyc | pdf_6a8faacca882a39304796eef402a5436_647a386eb012aa3d61c2e73303edf68c7410596022594182 |
| UDB | N-UNDECYLBENZENE | 正十一烷基苯 | 29463-63-6 | 1-Pheny/undecane | pdf_6a8faacca882a39304796eef402a5436_bc9a30293abd6ef6b62e1cfede859ec37410596022594182 |
| UDC | 1-UNDECENE | 1-十一烯 | 821-95-4 | n-Nonylethylenen | pdf_6a8faacca882a39304796eef402a5436_82c0a4c2babfb0015363e381ead56ed37410596022594182 |
| UND | UNDECANOL | 十一醇 | 112-42-5 | Alcohol C-11 (undeclic)Hendecanoic alcohol1-Hendeanol1-UndecanolUndecyl alcohol | pdf_6a8faacca882a39304796eef402a5436_e1a38d8aaab89e3e2bcfa524370e5c967410596022594182 |
| UPO | UREA PEROXIDE | 过氧化尿素 | 124-43-6 |  | pdf_6a8faacca882a39304796eef402a5436_1e8856ac1a6e83f799b8c06070a5daa27410596022594182 |
| URA | URANYL ACETATE | 乙酸铀酰 | 541-09-3 | Bis (Acetate) dioxouraniumUranium acetateUranium acetate dihydrodateUranium oxyc | pdf_6a8faacca882a39304796eef402a5436_b7f67a814f0fdacaabdddfc6657f53717410596022594182 |
| URE | UREA | 尿素 | 57-13-6 | CarbamideCarbonyldiamide | pdf_6a8faacca882a39304796eef402a5436_59ba458fd70778977a057110b8dea1137410596022594182 |
| URP | URANIUM PEROXIDE | 过氧化铀 |  | Uranium oxide peroxide(UO2)[O2])Uranium oxide (UO4) | pdf_6a8faacca882a39304796eef402a5436_9e5158b80be9fc4ad4ea75b016454e8c7410596022594182 |
| URS | URANYL SULFATE | 硫酸铀酰 | 1314-64-3 | Uranium sulfateUranium sulfate trihydrateUrany/ sulfate trihydrate | pdf_6a8faacca882a39304796eef402a5436_e262c036e28e678dd4dd2028af42b6de7410596022594182 |
| VAL | VALERALDEHYDE | 戊醛 | 110-62-3 |  | pdf_6a8faacca882a39304796eef402a5436_41ec261f15ad397263dbc81918f198dc7410596022594182 |
| VAM | VINYL ACETATE | 乙酸乙烯酯 | 108-05-4 | VAMVinyl A monomerVac | pdf_6a8faacca882a39304796eef402a5436_a006685ea5f5f41320f101f5692d65fe7410596022594182 |
| VBL | VANILLAN BLACK LIQUOR | 香草黑液 |  | UF oxylignin | pdf_6a8faacca882a39304796eef402a5436_5022f629c655981233c88c21f26ea4447410596022594182 |
| VCH | VINYL CYCLOHEXENE | 乙烯基环己烯 | 100-40-3 | 4-Vinyl-1-cyclochexene | pdf_6a8faacca882a39304796eef402a5436_3008765f1ea74f1589d9e5bc99c449ae7410596022594182 |
| VCI | VINYLIDENE CHLORIDE | 偏二氯乙烯 | 75-35-4 | 1,1-Dichloroethyleneunsym-Dichloroethylene | pdf_6a8faacca882a39304796eef402a5436_acb87e695ca5227c8699893b76a1ec617410596022594182 |
| VCM | VINYL CHLORIDE | 氯乙烯 | 75-01-4 |  | pdf_6a8faacca882a39304796eef402a5436_2814d5bc0020ca50f3f4dcd2b539d93c7410596022594182 |
| VEE | VINYL ETHYL ETHER | 乙烯基乙醚 | 109-92-2 | Ether, vinyl ethylEthyl vinyl etherVinamar | pdf_6a8faacca882a39304796eef402a5436_19c811198ca55789ef87a04732d731eb7410596022594182 |
| VFI | VINYL FLUORIDE | 氟乙烯 | 75-02-5 | FluorethyleneMonofluorethylene | pdf_6a8faacca882a39304796eef402a5436_73c28703dc7a9774cbc19f29f8a737e07410596022594182 |
| VME | VINYL METHYL ETHER | 乙烯基甲醚 | 107-25-5 | MethoxythyleneMethyl vinyl ether | pdf_6a8faacca882a39304796eef402a5436_2d808e0692d964d217172d1bf1a29a167410596022594182 |
| VND | VINYL NEODECANOATE | 新癸酸乙烯酯 | 51000-52-3 | Neodecanic acid, vinyl esterVV 10 vinyl monomer | pdf_6a8faacca882a39304796eef402a5436_4b417bc82321b00c692adcee1c4000657410596022594182 |
| VNO | VANADIUM OXIDE | 氧化钒 |  | Vanadium (V) oxideVanadium pentoxide | pdf_6a8faacca882a39304796eef402a5436_f16f54243bc2d6b2b3a033fa4b5744d27410596022594182 |
| VNT | VINYL TOLUENE | 乙烯基甲苯 | 611-15-4 | p-Methylstyrene | pdf_6a8faacca882a39304796eef402a5436_4ed7c705bf762c1fff1336618c35e5247410596022594182 |
| VOT | VANADIUM OXYTRICHLORIDE | 三氯氧钒 | 7727-18-6 | TrichlorooxovanadiumVanadyl chlorideVanadyl trichloride | pdf_6a8faacca882a39304796eef402a5436_8e43b06eb7f84ed81e511f06109522c17410596022594182 |
| VOX | VANADIUM PENTOXIDEvox | 五氧化二钒 |  | Vanadic anhydrideVanadium pentaoxide | pdf_6a8faacca882a39304796eef402a5436_8942215599930cac6ac12c28f8775dc67410596022594182 |
| VSF | VANADYL SULFATE | 硫酸氧钒 | 27774-13-6 | Vanadium oxysulfateVanadyl sulfate dihydrate | pdf_6a8faacca882a39304796eef402a5436_80970f0a86d838e12561db2d1327ce917410596022594182 |
| VTS | VINYLTRICHLOROSILANE | 乙烯基三氯硅烷 | 75-94-5 | TrichlorovinysilaneTrichlorovinysilaneVinyl silicontrichlorovinysilaneReacts vio | pdf_6a8faacca882a39304796eef402a5436_2dc11c32e4e594756f7244f51b6e2e367410596022594182 |
| WCA | WAXES: CARNAUBA | 巴西棕榈蜡 |  |  | pdf_6a8faacca882a39304796eef402a5436_f09a99b33bba1919cdb74735849966667410596022594182 |
| WPF | WAXES: PARAFFIN | 石蜡 |  | Petroleum wax | pdf_6a8faacca882a39304796eef402a5436_3c78d42af9a34200f254a79dd5457aae7410596022594182 |
| WSL | WHITE SPIRIT (LOW (15-20%) AROMATIC)wsl | 白油精（低芳烃） |  | SKDN | pdf_6a8faacca882a39304796eef402a5436_e758f45819b82dd1e39a469dc4bfd8217410596022594182 |
| XLM | M-XYLENE | 间二甲苯 | 108-38-3 | 1.3-DimethylbenzeneXylol | pdf_6a8faacca882a39304796eef402a5436_7e352e2a80f7f1292e85e160694bb9517410596022594182 |
| XLO | O-XYLENE | 邻二甲苯 | 95-47-6 | 1.2-DimethylbenzeneXytol | pdf_6a8faacca882a39304796eef402a5436_c080d48424999fc357c685d362d0e1e37410596022594182 |
| XLP | P-XYLENE | 对二甲苯 | 106-42-3 | 1.4-DimethylbenzeneXyloi | pdf_6a8faacca882a39304796eef402a5436_6bd0495e82259a3fbbf6c94a5f1b94567410596022594182 |
| XYL | XYLENOL | 二甲酚 | 526-75-0 | Cresylic acidDimethylphenol2-Hydroxy-m-xylene2.6-Xylenol | pdf_6a8faacca882a39304796eef402a5436_0dfbf8c6ddb165ca75857fa4d648355f7410596022594182 |
| ZAC | ZINC AMMONIUM CHLORIDE | 氯化锌铵 | 14639-97-5 | Ammonium pentachlorozicateAmmonium zinc chloride | pdf_6a8faacca882a39304796eef402a5436_13fca2e62e1a0e6607d3a45aeea37b857410596022594182 |
| ZAR | ZINC ARSENATE | 砷酸锌 | 13464-33-0 |  | pdf_6a8faacca882a39304796eef402a5436_5917c5dad8422bf768d2b5906e9064dc7410596022594182 |
| ZBC | ZINC BICROMATE | 重铬酸锌 |  | Zinc dichromate | pdf_6a8faacca882a39304796eef402a5436_b765011ed2f7cf75ef563a30e4cbdbe87410596022594182 |
| ZBO | ZINC BORATE | 硼酸锌 | 14720-55-9 |  | pdf_6a8faacca882a39304796eef402a5436_f6ae672a3d8b4f4f833a12b3363482ff7410596022594182 |
| ZBR | ZINC BROMIDE | 溴化锌 | 7699-45-8 |  | pdf_6a8faacca882a39304796eef402a5436_2b10d6fb89c26996560e7f40c7f64efe7410596022594182 |
| ZCA | ZIRCONIUM ACETATE | 乙酸锆 | 7585-20-8 | Zirconium acetate solution | pdf_6a8faacca882a39304796eef402a5436_3f779718afc0fbffd70684d4bd723aed7410596022594182 |
| ZCB | ZINC CARBONATE | 碳酸锌 | 3486-35-9 | CalamineSmithsonite | pdf_6a8faacca882a39304796eef402a5436_2f7c722f997901f80bf6277a17feec437410596022594182 |
| ZCL | ZINC CHLORIDE | 氯化锌 | 7646-85-7 |  | pdf_6a8faacca882a39304796eef402a5436_eb6fa9f9d9588a8a1134004dc04467237410596022594182 |
| ZCN | ZINC CYANIDE | 氰化锌 |  | Cyanide d’zincZinc d’icyaride | pdf_6a8faacca882a39304796eef402a5436_af006cf6566ee06ac6f92ba19b90fdb17410596022594182 |
| ZCO | ZIRCONIUM OXYCHLORIDE | 氧氯化锆 | 7699-43-6 | Basic zirconium chlorideZirconium oxide chlorideZirconium oxychloride hydrateZir | pdf_6a8faacca882a39304796eef402a5436_a67538cb7f00710fe46d00e772d3ce387410596022594182 |
| ZCR | ZINC CHROMATE | 铬酸锌 | 13530-65-9 |  | pdf_6a8faacca882a39304796eef402a5436_d7d0dec097e3d3db18cba2f6a29a69d47410596022594182 |
| ZCS | ZIRCONIUM SULFATEzcs | 硫酸锆 |  | Disfilutatozronic acidZirconium sulfate tetrahydrate | pdf_6a8faacca882a39304796eef402a5436_48c11fefcf989ae69256f2c178704de97410596022594182 |
| ZCT | ZIRCONIUM TETRACHLORIDE | 四氯化锆 | 11126-30-0 | TetrachlorozirconiumZirconium chlorideZirconium tetrachloride solid(DOT) | pdf_6a8faacca882a39304796eef402a5436_6590bb5f87ea33c715db2f56c8920b217410596022594182 |
| ZDP | ZINC DIALKYLDITHIOPHOSPHATE | 二烷基二硫代磷酸锌 | 69993-19-7 |  | pdf_6a8faacca882a39304796eef402a5436_d744498cfd177f7135b7604437776a387410596022594182 |
| ZEC | ZECTRAN | 猛杀威（泽克特兰） | 315-18-4 | MexacarbateZactranZectaneZextran | pdf_6a8faacca882a39304796eef402a5436_16d3adc68e964bf3b8bc94a724071c0d7410596022594182 |
| ZFB | ZINC FLUOROBORATE | 氟硼酸锌 | 13826-88-5 | Zinc fluoborate solution | pdf_6a8faacca882a39304796eef402a5436_bfdabedf14032d3aa4d5bd7bd9c4faed7410596022594182 |
| ZFM | ZINC FORMATE | 甲酸锌 | 557-41-5 | Formic acid, zinc salt | pdf_6a8faacca882a39304796eef402a5436_492baa4e1678e0073134470aeb2af7a27410596022594182 |
| ZFX | ZINC FLUORIDE | 氟化锌 | 573640-07-0 | Zinc difluoride | pdf_6a8faacca882a39304796eef402a5436_283865e04b03a3fa4061d2da87c6714b7410596022594182 |
| ZHS | ZINC HYDROSULFITE | 连二亚硫酸锌 | 7779-86-4 | Zinc dithionte | pdf_6a8faacca882a39304796eef402a5436_97f5b7f1938099d73bf435fc02bbade47410596022594182 |
| ZIR | ZIRCONIUM NITRATEzir | 硝酸锆 |  | Zirconium nitrate pentahydrate | pdf_6a8faacca882a39304796eef402a5436_82ad9cbf9b1a1db77344f809990d58607410596022594182 |
| ZNA | ZINC ACETATE | 乙酸锌 | 557-34-6 | Acatic acid, zinc saltDicarbomethoxyzineDinc acetate difydrateZinc diacetate | pdf_6a8faacca882a39304796eef402a5436_0ab02cd55386482f4e76f3f6b6ab89387410596022594182 |
| ZNT | ZINC NITRATE | 硝酸锌 | 7779-88-6 | Zinc nitrate hexahydrate | pdf_6a8faacca882a39304796eef402a5436_6c1f45e61b2779e11d3c897bcce3a88d7410596022594182 |
| ZPC | ZINC POTASSIUM CHROMATE | 铬酸锌钾 | 11103-86-9 | Potassium zinc chromateZinc yellow Y-539-D | pdf_6a8faacca882a39304796eef402a5436_ca9f01ff5f04d825b83a9e0d359796e77410596022594182 |
| ZPF | ZIRCONIUM POTASSIUM FLOURIDE | 氟锆酸钾 |  | Potassium fluorizconatePotassium hexaffluoricronatePotassium zirconium fluoride | pdf_6a8faacca882a39304796eef402a5436_25b6e1ba50c1ec7fa0c7c5eefabebe9e7410596022594182 |
| ZPP | ZINC PHOSPHIDE | 磷化锌 | 1314-84-7 |  | pdf_6a8faacca882a39304796eef402a5436_881da10e7148756f9e529abf3201325f7410596022594182 |
| ZPS | ZINC PHENOLSULFONATE | 苯酚磺酸锌 | 127-82-2 | Zinc phenolsulfonateoctahydrateZinc p-phenolsulfonateZinc sulfocarbolateZinc sul | pdf_6a8faacca882a39304796eef402a5436_0e31b79c7cf7c806974c6d1914096d147410596022594182 |
| ZSF | ZINC SULFATE | 硫酸锌 | 7733-02-0 |  | pdf_6a8faacca882a39304796eef402a5436_c41473d3ead3ee2de9e0bdafc15212fb7410596022594182 |
| ZSL | ZINC SILICOFLUORIDE | 氟硅酸锌 |  | Zinc flussilicate Zinc hexfluorosilicate Zinc silcolfluoride hexahydrate | pdf_6a8faacca882a39304796eef402a5436_4ab4daf73be7f26734f62b2f2c40ea3c7410596022594182 |

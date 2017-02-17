// Скрипт проверяет состояние локальной базы данных getmyad (которая используется worker'ами)
// При необходимости восстанавливает
if (!db.log.impressions.validate().valid || !db.log.impressions.stats().capped) {
	print ("Database log.impressions broken, recreating collections");	
	db.log.impressions.drop();
	db.createCollection('log.impressions', {capped: true, max: 1000000, size: 635000000});
	db.log.impressions.ensureIndex({'token': 1});
	db.log.impressions.ensureIndex({'ip': 1,'cookie':1});
}
if (!db.log.impressions.block.validate().valid || !db.log.impressions.block.stats().capped) {
	print ("Database log.impressions.block broken, recreating collections");	
	db.log.impressions.block.drop();
	db.createCollection('log.impressions.block', {capped: true, max: 1000000, size: 635000000});
}

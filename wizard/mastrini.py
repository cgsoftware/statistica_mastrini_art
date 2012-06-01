# -*- encoding: utf-8 -*-

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _
from datetime import datetime, timedelta
import base64
from tempfile import TemporaryFile
import math

class tempstatistiche_mastriniart(osv.osv):
    
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True
    
    
    _name = 'tempstatistiche.mastriniart'
    _description = 'temporaneo statistica mastrini articoli'
    _columns = {######################################################
                ##################PARAMETRI###########################
                'p_dadata': fields.datetime('Da Data', required=True  ),
                'p_adata':fields.datetime('A Data', required=True  ),
                'p_magazzino_id':fields.many2one('stock.location', 'Deposito', required=False),
                'p_magazzino_name':fields.char('Magazzino', size= 100),
                'p_categoria_id':fields.many2one('product.category', 'Categoria', required=False),
                'p_categoria_name':fields.char('Categoria', size= 100),
                'p_articolo_id':fields.many2one('product.product', 'Articolo', required=False),
                'p_articolo_name':fields.char('Categoria', size= 100),
                'p_export_csv':fields.char('CSV', size=2),
                #####################################################
                #####################################################
                'articolo_id':fields.many2one('product.product', 'Articolo'),
                'desc':fields.char('Descrizione', size= 100),
                'uom':fields.many2one('product.uom',' UM'),
                'giac_iniz':fields.float('Giacenza Iniziale', digits=(25,4)),
                'desc_move':fields.char('Descrizione', size= 50),
                'qta_mov':fields.float('Quantita', digits=(25,4)),
                'data_move':fields.date('DataMovimento'),
               
                'giac_finale':fields.float('Giacenza Finale', digits=(25,4)),
                'doc_id':fields.many2one('fiscaldoc.header', 'Documento'),
                'num_doc':fields.char('Numero Documento', size= 50),
                'cliente': fields.char('Numero Documento', size= 50),
                'data_doc':fields.date('Data Documento'),
                'valore':fields.float('Valore', digits=(25,4)),
                'move_id':fields.many2one('stock.move'),  
                
                'entrate':fields.float('Aumenti', digits=(25,4)),
                'uscite':fields.float('Uscite', digits=(25,4)),
                      
                }
    _order = 'articolo_id, data_move '
    
    
    def mappa_categoria(self, cr, uid, categoria, context):
            lista_id=[]
       
        #for categ in categoria.categoria_id: 
            lista_id.append(categoria.categoria_id.id)
            #import pdb;pdb.set_trace()
            if categoria.categoria_id.child_id:
                for child in categoria.categoria_id.child_id:
                    lista_id.append(child.id)
                    if child.child_id:
                        for figlio in child.child_id:
                            lista_id.append(figlio.id)
                    
                    
        
            return lista_id
    
    def carica_doc(self, cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
        move_obj=self.pool.get('stock.move')
        cerca = [('type', '<>', 'service')]
        context['from_date'] = parametri.dadata
        context['to_date'] = parametri.adata
        context['location']= parametri.magazzino_id.id
        p_dadata = parametri.dadata
        p_adata = parametri.adata
        p_magazzino_id = parametri.magazzino_id.id
        p_magazzino_name = parametri.magazzino_id.name
        
        if parametri.articolo_id:
            cerca.append(('id','=',parametri.articolo_id.id))
        if parametri.categoria_id:
            #TODO RAGIONARE SU CATEGORIE.....
            lista_id=[]
            lista_id = self.mappa_categoria(cr, uid, parametri, context)
            cerca.append(('categ_id','in', lista_id))
        
#        import pdb;pdb.set_trace()
        
        product_ids = self.pool.get('product.product').search(cr,uid,cerca,context=context)
        
        if product_ids:
            #product = self.pool.get('product.product').browse(cr,uid,product_ids[0],context=context)
           
            for product in self.pool.get('product.product').browse(cr,uid,product_ids,context=context):
                giac_finale = giac_ini = product.qty_available
                entrate = uscite = 0
                cliente = doc = ''
                #esistenza = product.qty_available
                cerca_move = [('product_id','=',product.id),('state','=','done'),('date','<=',p_adata),('date','>=',p_dadata)]
                move_ids = move_obj.search(cr, uid, cerca_move, context=context)
                if move_ids:
                    for move in move_obj.browse(cr, uid, move_ids, context=context):
                        #TESTO SE IL MOVIMENTO E' IN ENTRATA
                        if move.location_id.id == parametri.magazzino_id.id:
                            #DOCUMENTO DI VENDITA LA MERCE ESCE DAL MAGAZZINO
                            # LA MOVIMENTAZIONE È NEGATIVA 
                            giac_ini += move.product_qty
#                            import pdb;pdb.set_trace()
                            uscite = move.product_qty
                            
                            if move.picking_id.partner_id:
                                cliente = move.picking_id.partner_id.name
                            if move.picking_id.doc_id:
                                doc = move.picking_id.doc_id.id
                            riga_wr = {
                                       'p_dadata': p_dadata,
                                       'p_adata':p_adata,
                                       'p_magazzino_id': parametri.magazzino_id.id,
                                       'p_magazzino_name':parametri.magazzino_id.complete_name,
                                       'p_categoria_id':parametri.categoria_id.id,
                                       'p_categoria_name':parametri.categoria_id.name,
                                       'p_articolo_id':parametri.articolo_id.id ,
                                       'p_articolo_name':parametri.articolo_id.name_template,
                               
                                       'articolo_id':product.id,
                                       'desc':str(product.default_code)+'-'+str(product.name_template)+'-'+str(product.variants),
                                       'uom':product.product_tmpl_id.uom_id.id,
                                       'giac_iniz':giac_ini,
                               
                                       'move_id': move.id,
                                       'desc_move':move.name,
                                       'qta_mov': move.product_qty*-1,
                                       'data_move':move.date,
                
                                       'giac_finale': giac_finale, #esistenza - move.product_qty ,
                                       'cliente':cliente,
                                       
                                       'doc_id':doc,
                                       'uscite':uscite,
                                       #'num_doc':fields.char('Numero Documento', size= 50),
                                       #'data_doc':fields.date('Data Documento'),
                                       #'valore':fields.float('Valore', digits=(25,4))
                               }
                            ok = self.create(cr,uid,riga_wr)
                        if move.location_dest_id.id == parametri.magazzino_id.id:
                            #PRODUZIONE DI MERCE MOVIMENTAZIONE POSITIVA 
                            #VÀ SOTTRATTA ALLA GIACENZA FINALE
                            giac_ini -= move.product_qty
                            entrate = move.product_qty
                            cliente = ''
                            if move.picking_id.partner_id:
                                cliente = move.picking_id.partner_id.name
                            if move.picking_id.doc_id:
                                doc = move.picking_id.doc_id.id
                            riga_wr = {
                                       'p_dadata': p_dadata,
                                       'p_adata':p_adata,
                                       'p_magazzino_id': parametri.magazzino_id.id,
                                       'p_magazzino_name':parametri.magazzino_id.complete_name,
                                       'p_categoria_id':parametri.categoria_id.id,
                                       'p_categoria_name':parametri.categoria_id.name,
                                       'p_articolo_id':parametri.articolo_id.id ,
                                       'p_articolo_name':parametri.articolo_id.name_template,
                               
                                       'articolo_id':product.id,
                                       'desc':str(product.default_code)+'-'+str(product.name_template)+'-'+str(product.variants),
                                       'uom':product.product_tmpl_id.uom_id.id,
                                       'giac_iniz':giac_ini,
                               
                                       'move_id': move.id,
                                       'desc_move':move.name,
                                       'qta_mov': move.product_qty,
                                       'data_move':move.date,
                                       'giac_finale': giac_finale, #esistenza + move.product_qty ,
                                       
                                       'cliente':cliente,
                                       
                                       'doc_id':doc,
                                       'entrate':entrate,
                                       #'doc_id':fields.many2one('fiscaldoc.header', 'Documento'),
                                       #'num_doc':fields.char('Numero Documento', size= 50),
                                       #'data_doc':fields.date('Data Documento'),
                                       #'valore':fields.float('Valore', digits=(25,4))
                               }
                            ok = self.create(cr,uid,riga_wr)
            
            
            
            
#                pass
        return
          
        
    
    
tempstatistiche_mastriniart()

class stampa_stat_mastrini(osv.osv_memory):
    _name = 'stampa.stat.mastrini'
    _description = 'par. stampa per la stat. mastrini'
    _columns = {'dadata': fields.datetime('Da Data', required=True  ),
                'adata':fields.datetime('A Data', required=True  ),
                'magazzino_id':fields.many2one('stock.location', 'Deposito', required=True),
                'categoria_id':fields.many2one('product.category', 'Categoria', required=False),
                'articolo_id':fields.many2one('product.product', 'Articolo', required=False),
                'export_csv':fields.boolean('Genera CSV')
                }

    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        pool = pooler.get_pool(cr.dbname)
        active_ids = context and context.get('active_ids', [])
        parametri = self.browse(cr,uid,ids)[0]
        #data['form']['parameters'] = parametri
        
        return {'type': 'ir.actions.report.xml',
                'report_name': 'mastrini',
                'datas': data,
                }
    
    def check_report(self, cr, uid, ids, context=None):
        #
        if context is None:
            context = {}
        data = {}
        parametri = self.browse(cr,uid,ids)[0]             
        
        ok = self.pool.get('tempstatistiche.mastriniart').carica_doc(cr,uid,parametri,context)
        
        if parametri.export_csv:
            return  {
                             'name': 'Export Mastrini Articoli',
                             'view_type': 'form',
                             'view_mode': 'form',
                             'res_model': 'crea_csv_mastrini_art',
                             'type': 'ir.actions.act_window',
                             'target': 'new',
                             'context': context                            
                             
                             }
        else:
            return self._print_report(cr, uid, ids, data, parametri, context=context)
    
        return
        
        
    def view_init(self, cr, uid, fields_list, context=None):
       
        res = super(stampa_ordini, self).view_init(cr, uid, fields_list, context=context)

        return res
    
             
    def  default_get(self, cr, uid, fields, context=None):
       
        pool = pooler.get_pool(cr.dbname)
        docs = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])

        return {}
        
    
stampa_stat_mastrini()

class crea_csv_mastrini(osv.osv_memory):
    _name = "crea_csv_mastrini_art"
    _description = "Crea il csv dal temporaneo mastrini articoli"
    _columns = {
                    'state': fields.selection((('choose', 'choose'), # choose accounts
                                               ('get', 'get'), # get the file
                                   )),
                    #'nomefile':fields.char('Nome del file',size=20,required = True)
                    'data': fields.binary('File', readonly=True),

                    }
    _defaults = {
                 'state': lambda * a: 'choose',
                 }
    
    def generacsvmastriniart(self, cr, uid, ids,context=None):
        if ids:
            stampa_obj = self.pool.get('tempstatistiche.mastriniart')
            parametri = stampa_obj.browse(cr, uid, ids)[0]
            idts = self.pool.get('tempstatistiche.mastriniart').search(cr,uid,[])
            if idts:
                File = """"""""
                Record =""
                Record += '"'+"Articolo"+'";'
                Record += '"'+"Giacenza_Iniziale"+'";'
                Record += '"'+"Giacenza_Finale"+'";'
                Record += '"'+"Data"+'";'
                Record += '"'+"Descrizione"+'";'
                Record += '"'+"Cliente"+'";'
                Record += '"'+"Quantita"+'";'
                Record += "\r\n"
                for riga in self.pool.get('tempstatistiche.mastriniart').browse(cr,uid,idts, context):
                    Record += '"'+ riga.desc +'";'
                    Record += '"'+ str(riga.giac_iniz) +'";'
                    Record += '"'+ str(riga.giac_finale) +'";'
                    
                    data = riga.data_move
                    data = time.strptime(data, "%Y-%m-%d")
                    data = time.strftime("%d/%m/%Y",data)
                    Record += '"'+ data +'";' 
                    Record += '"'+ riga.desc_move +'";'
                    Record += '"'+ riga.cliente +'";'
                    Record += '"'+ str(riga.qta_mov) +'";'
                    Record += "\r\n"
                #import pdb;pdb.set_trace()
                File += Record
                out = base64.encodestring(File)   
                           
                return self.write(cr, uid, ids, {'state':'get', 'data':out}, context=context)
            else:
                return {'type': 'ir.actions.act_window_close'}
crea_csv_mastrini()
from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEXT_UPLOAD_FOLDER'] = 'text_uploads'

# 确保上传目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['TEXT_UPLOAD_FOLDER']):
    os.makedirs(app.config['TEXT_UPLOAD_FOLDER'])

def read_text_content(filename):
    """读取文本文件内容"""
    if not filename:
        return ""
    
    filepath = os.path.join(app.config['TEXT_UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "文件不存在"
    
    try:
        # 对于.txt文件
        if filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        # 对于.docx文件
        elif filename.endswith('.docx'):
            try:
                from docx import Document
                doc = Document(filepath)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                return "需要安装python-docx库来读取.docx文件"
        # 对于其他格式
        else:
            return "不支持的文件格式"
    except Exception as e:
        return f"读取文件出错: {str(e)}"

# 初始化数据库
def init_db():
    conn = sqlite3.connect('audio_records.db')
    c = conn.cursor()
    
    # 删除旧表（如果存在）
    c.execute('DROP TABLE IF EXISTS audio_records')
    c.execute('DROP TABLE IF EXISTS text_records')
    
    # 创建新的音频记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS audio_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            language TEXT NOT NULL,
            sample_rate TEXT NOT NULL,
            channels TEXT NOT NULL,
            status TEXT NOT NULL,
            upload_time DATETIME NOT NULL,
            uploader TEXT NOT NULL,
            text_filename TEXT
        )
    ''')
    
    # 创建新的文本记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS text_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            language TEXT NOT NULL,
            status TEXT NOT NULL,
            upload_time DATETIME NOT NULL,
            uploader TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio[]' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    files = request.files.getlist('audio[]')
    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    language = request.form.get('language')
    sample_rate = request.form.get('sample_rate')
    channels = request.form.get('channels')
    uploader = "admin"  # 这里可以根据实际需求修改为真实的用户系统
    
    uploaded_files = []
    conn = sqlite3.connect('audio_records.db')
    c = conn.cursor()
    
    try:
        for file in files:
            if file and file.filename:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                uploaded_files.append(file.filename)
                
                # 检查是否存在对应的文本文件
                base_filename = os.path.splitext(file.filename)[0]
                c.execute('SELECT filename FROM text_records WHERE filename LIKE ?', (f"{base_filename}%",))
                text_record = c.fetchone()
                text_filename = text_record[0] if text_record else None
                
                # 记录到数据库
                c.execute('''
                    INSERT INTO audio_records 
                    (filename, language, sample_rate, channels, status, upload_time, uploader, text_filename)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file.filename, 
                    language, 
                    sample_rate, 
                    channels, 
                    '上传成功',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    uploader,
                    text_filename
                ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({
        'message': '文件上传成功',
        'files': uploaded_files,
        'language': language,
        'sample_rate': sample_rate,
        'channels': channels,
        'total_files': len(uploaded_files)
    })

@app.route('/upload_text', methods=['POST'])
def upload_text():
    if 'text[]' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    files = request.files.getlist('text[]')
    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    language = request.form.get('language')
    uploader = "admin"  # 这里可以根据实际需求修改为真实的用户系统
    
    uploaded_files = []
    conn = sqlite3.connect('audio_records.db')
    c = conn.cursor()
    
    try:
        for file in files:
            if file and file.filename:
                filename = os.path.join(app.config['TEXT_UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                uploaded_files.append(file.filename)
                
                # 记录到数据库
                c.execute('''
                    INSERT INTO text_records 
                    (filename, language, status, upload_time, uploader)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    file.filename, 
                    language,
                    '上传成功',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    uploader
                ))
                
                # 更新对应的音频记录
                base_filename = os.path.splitext(file.filename)[0]
                c.execute('''
                    UPDATE audio_records 
                    SET text_filename = ? 
                    WHERE filename LIKE ?
                ''', (file.filename, f"{base_filename}%"))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({
        'message': '文件上传成功',
        'files': uploaded_files,
        'language': language,
        'total_files': len(uploaded_files)
    })

@app.route('/records', methods=['GET'])
def get_records():
    conn = sqlite3.connect('audio_records.db')
    c = conn.cursor()
    
    # 获取音频记录
    c.execute('SELECT * FROM audio_records ORDER BY upload_time DESC')
    audio_records = [{
        'id': r[0],
        'filename': r[1],
        'language': r[2],
        'sample_rate': r[3],
        'channels': r[4],
        'status': r[5],
        'upload_time': r[6],
        'uploader': r[7],
        'text_filename': r[8] or '未关联标注文本',
        'text_content': read_text_content(r[8]) if r[8] else '无标注内容'
    } for r in c.fetchall()]
    
    # 获取文本记录
    c.execute('SELECT * FROM text_records ORDER BY upload_time DESC')
    text_records = [{
        'id': r[0],
        'filename': r[1],
        'language': r[2],
        'status': r[3],
        'upload_time': r[4],
        'uploader': r[5]
    } for r in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'audio_records': audio_records,
        'text_records': text_records
    })

@app.route('/delete_audio', methods=['POST'])
def delete_audio():
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': '未提供要删除的记录ID'}), 400
            
        ids = data['ids']
        if not isinstance(ids, list):
            return jsonify({'error': '无效的ID格式'}), 400
            
        conn = sqlite3.connect('audio_records.db')
        c = conn.cursor()
        
        # 获取要删除的文件名列表
        c.execute('SELECT filename FROM audio_records WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
        files_to_delete = c.fetchall()
        
        # 从数据库中删除记录
        c.execute('DELETE FROM audio_records WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
        conn.commit()
        
        # 删除实际文件
        for file_record in files_to_delete:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record[0])
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return jsonify({
            'message': f'成功删除 {len(ids)} 条记录',
            'deleted_ids': ids
        })
        
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/delete_text', methods=['POST'])
def delete_text():
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': '未提供要删除的记录ID'}), 400
            
        ids = data['ids']
        if not isinstance(ids, list):
            return jsonify({'error': '无效的ID格式'}), 400
            
        conn = sqlite3.connect('audio_records.db')
        c = conn.cursor()
        
        # 获取要删除的文件名列表
        c.execute('SELECT filename FROM text_records WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
        files_to_delete = c.fetchall()
        
        # 从数据库中删除记录
        c.execute('DELETE FROM text_records WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
        
        # 更新关联的音频记录
        for file_record in files_to_delete:
            c.execute('UPDATE audio_records SET text_filename = NULL WHERE text_filename = ?', (file_record[0],))
        
        conn.commit()
        
        # 删除实际文件
        for file_record in files_to_delete:
            file_path = os.path.join(app.config['TEXT_UPLOAD_FOLDER'], file_record[0])
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return jsonify({
            'message': f'成功删除 {len(ids)} 条记录',
            'deleted_ids': ids
        })
        
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True) 
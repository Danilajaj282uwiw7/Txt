// Project: DB2Text Lite // Updated with purple UI + footer credit

// ============================= // MainActivity.kt (UPDATED UI) // ============================= package com.db2text.lite

import android.app.Activity import android.content.Intent import android.database.sqlite.SQLiteDatabase import android.graphics.Color import android.net.Uri import android.os.Bundle import android.view.Gravity import android.widget.* import androidx.appcompat.app.AppCompatActivity import java.io.File

class MainActivity : AppCompatActivity() {

private lateinit var status: TextView
private var dbUri: Uri? = null

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    val mainLayout = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setBackgroundColor(Color.parseColor("#1E1B2E"))
        setPadding(32, 64, 32, 32)
    }

    val title = TextView(this).apply {
        text = "DB2Text Lite"
        textSize = 24f
        setTextColor(Color.parseColor("#C084FC"))
        gravity = Gravity.CENTER
    }

    val pickBtn = Button(this).apply {
        text = "Выбрать файл"
        setBackgroundColor(Color.parseColor("#7C3AED"))
        setTextColor(Color.WHITE)
    }

    val convertBtn = Button(this).apply {
        text = "Конвертировать"
        setBackgroundColor(Color.parseColor("#9333EA"))
        setTextColor(Color.WHITE)
    }

    status = TextView(this).apply {
        text = "Ожидание..."
        setTextColor(Color.LTGRAY)
        gravity = Gravity.CENTER
    }

    val footer = TextView(this).apply {
        text = "creator: @xeexile"
        textSize = 12f
        setTextColor(Color.GRAY)
        gravity = Gravity.CENTER
    }

    mainLayout.addView(title)
    mainLayout.addView(pickBtn)
    mainLayout.addView(convertBtn)
    mainLayout.addView(status)

    val spacer = Space(this).apply {
        layoutParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            0,
            1f
        )
    }

    mainLayout.addView(spacer)
    mainLayout.addView(footer)

    setContentView(mainLayout)

    pickBtn.setOnClickListener {
        val intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.type = "*/*"
        startActivityForResult(intent, 1)
    }

    convertBtn.setOnClickListener {
        dbUri?.let { uri ->
            val file = File(cacheDir, "temp.db")
            contentResolver.openInputStream(uri)?.use { input ->
                file.outputStream().use { output ->
                    input.copyTo(output)
                }
            }

            val outFile = File(getExternalFilesDir(null), "output.txt")
            exportDatabaseToTxt(file.absolutePath, outFile.absolutePath)

            status.text = "Готово: ${outFile.absolutePath}"
        } ?: run {
            status.text = "Сначала выбери файл"
        }
    }
}

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    if (requestCode == 1 && resultCode == Activity.RESULT_OK) {
        dbUri = data?.data
        status.text = "Файл выбран"
    }
}

private fun exportDatabaseToTxt(dbPath: String, outputPath: String) {
    val db = SQLiteDatabase.openDatabase(dbPath, null, SQLiteDatabase.OPEN_READONLY)
    val file = File(outputPath)
    val writer = file.bufferedWriter()

    val cursorTables = db.rawQuery("SELECT name FROM sqlite_master WHERE type='table'", null)

    while (cursorTables.moveToNext()) {
        val tableName = cursorTables.getString(0)
        writer.write("TABLE: $tableName\n")

        val cursor = db.rawQuery("SELECT * FROM $tableName", null)
        val columns = cursor.columnNames

        writer.write(columns.joinToString(", ") + "\n")

        while (cursor.moveToNext()) {
            val row = columns.map { col ->
                val index = cursor.getColumnIndex(col)
                if (index >= 0) cursor.getString(index) else ""
            }
            writer.write(row.joinToString(", ") + "\n")
        }

        writer.write("\n\n")
        cursor.close()
    }

    cursorTables.close()
    writer.close()
    db.close()
}

}

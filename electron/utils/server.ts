/**
 * ****************************************************************************
 *  @author      xqyjlj
 *  @file        server.ts
 *  @brief
 *
 * ****************************************************************************
 *  @attention
 *  Licensed under the Apache License v. 2 (the "License");
 *  You may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0.html
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *  Copyright (C) 2025-2025 xqyjlj<xqyjlj@126.com>
 *
 * ****************************************************************************
 *  Change Logs:
 *  Date           Author       Notes
 *  ------------   ----------   -----------------------------------------------
 *  2025-10-20     xqyjlj       initial version
 */

import type { Buffer } from 'node:buffer'
import { spawn } from 'node:child_process'
import axios from 'axios'
import { app } from 'electron'
import * as path from 'node:path'
import * as fs from 'node:fs'
import { processArgs } from './args'
import { getServerFolder } from './settings'

export function clientOnline(url: string) {
  if (!app.isPackaged) {
    return
  }

  axios.get(`${url}/api/client/online`, { params: { id: process.pid } })
    .then(() => {
    })
    .catch((error) => {
      console.error('clientOnline Error:', error.message)
    })
}

export function clientOffline(url: string) {
  if (!app.isPackaged) {
    return
  }

  axios.get(`${url}/api/client/offline`, { params: { id: process.pid } })
    .then(() => {
    })
    .catch((error) => {
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNRESET') {
          /* !< 服务端已经断开 */
          return
        }
      }
      console.error('clientOffline Error:', error.message)
    })
}

export function createServer(): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!app.isPackaged) {
      resolve(processArgs.backendUrl)
      return
    }

    try {
      const serverFolder = getServerFolder()
      const exePath = path.join(serverFolder, 'csp-server.exe')
      const pyPath = path.join(serverFolder, 'csp-server.py')

      console.log('Server folder:', serverFolder)
      console.log('Checking for csp-server.exe:', fs.existsSync(exePath))
      console.log('Checking for csp-server.py:', fs.existsSync(pyPath))

      let process
      let commandUsed
      
      if (fs.existsSync(exePath)) {
        console.log('Using csp-server.exe')
        commandUsed = 'csp-server.exe'
        process = spawn('csp-server.exe', ['serve', '-p', '55432'], {
          cwd: serverFolder,
        })
      } else if (fs.existsSync(pyPath)) {
        console.log('Using csp-server.py with python')
        commandUsed = 'python csp-server.py'
        process = spawn('python', ['csp-server.py', 'serve', '-p', '55432'], {
          cwd: serverFolder,
        })
      } else {
        const errorMsg = 'Neither csp-server.exe nor csp-server.py found'
        console.error(errorMsg)
        console.error('Files in server folder:', fs.readdirSync(serverFolder))
        reject(new Error(errorMsg))
        return
      }

      let resolved = false

      const timeout = setTimeout(() => {
        if (!resolved) {
          resolved = true
          const errorMsg = `Server startup timeout after 5s using ${commandUsed}`
          console.error(errorMsg)
          process.kill()
          reject(new Error(errorMsg))
        }
      }, 5000)

      process.stdout!.on('data', (data: Buffer) => {
        console.log('Server stdout:', data.toString())
      })

      process.stderr!.on('data', (data: Buffer) => {
        const text = data.toString()
        console.log('Server stderr:', text)
        const match = text.match(/http:\/\/127\.0\.0\.1:(\d+)/)
        if (match) {
          const url = match[0]
          resolved = true
          clearTimeout(timeout)
          console.log('Server started successfully at:', url)
          /* !< 延时 1s 等待服务端真正启动 */
          setTimeout(() => {
            clientOnline(url)
            resolve(url)
          }, 1000)
        }
      })

      process.once('error', (err) => {
        if (!resolved) {
          resolved = true
          clearTimeout(timeout)
          const errorMsg = `Failed to spawn server process: ${err.message}`
          console.error(errorMsg)
          reject(new Error(errorMsg))
        }
      })

      process.once('exit', (code) => {
        if (!resolved) {
          resolved = true
          clearTimeout(timeout)
          const errorMsg = `Server exited with code ${code} using ${commandUsed}`
          console.error(errorMsg)
          reject(new Error(errorMsg))
        }
      })
    }
    catch (error) {
      const errorMsg = `Error in createServer: ${error instanceof Error ? error.message : String(error)}`
      console.error(errorMsg)
      reject(new Error(errorMsg))
    }
  })
}

